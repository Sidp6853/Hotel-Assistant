    import json
    import uuid
    import sqlite3
    import logging
    from typing import TypedDict, List, Dict, Any
    from datetime import datetime

    from pydantic import BaseModel, Field, ValidationError

    from langchain_ollama import ChatOllama  # FIXED: Updated import
    from langgraph.graph import StateGraph, END

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def safe_json_load(content: str) -> dict:
        """
        Safely parse JSON from LLM output.
        Handles ```json blocks and trailing text.
        """
        try:
            content = content.strip()
            if content.startswith("```json"):
                # Extract content between ```json and ```
                parts = content.split("```")
                if len(parts) >= 3:
                    content = parts[1].replace("json", "").strip()
            elif content.startswith("```"):
                content = content.split("```")[1].strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Content: {content[:200]}")
            raise ValueError(f"Invalid JSON from model: {e}")


    class AnalysisOutput(BaseModel):
        severity_level: str
        category: str
        sentiment_score: float
        escalation_required: bool
        key_issues: List[str]
        summary_reasoning: str = Field(
            description="Concise justification without step-by-step reasoning"
        )


    class ActionItem(BaseModel):
        action: str
        responsible: str
        priority: str = "normal"


    class ActionPlanOutput(BaseModel):
        internal_actions: List[ActionItem]
        assigned_department: str
        estimated_resolution_time: str


    class ResponseOutput(BaseModel):
        guest_response: str

    class ComplaintState(TypedDict):
        complaint_id: str
        guest_name: str
        room_number: str
        contact_info: str
        complaint_text: str

        analysis: Dict[str, Any]
        actions: Dict[str, Any]
        response: Dict[str, Any]

        stored_successfully: bool
        notification_sent: bool

    llm = ChatOllama(
        model="llama3.2:3b",
        temperature=0.3,
        num_predict=512,
    )


    def analysis_agent(state: ComplaintState) -> ComplaintState:
        logger.info(" Analysis Agent running")

        prompt = f"""Analyze this hotel complaint. Return ONLY valid JSON:

    {{
    "severity_level": "low|medium|high|critical",
    "category": "brief category",
    "sentiment_score": -1.0 to 1.0,
    "escalation_required": true|false,
    "key_issues": ["issue1", "issue2"],
    "summary_reasoning": "one sentence"
    }}

    Complaint: {state['complaint_text']}

    JSON:"""

        try:
            result = llm.invoke(prompt)
            data = safe_json_load(result.content)
            validated = AnalysisOutput(**data)
            state["analysis"] = validated.model_dump()
            logger.info(f"✅ Analysis complete: {state['analysis']['severity_level']}")
        except (ValidationError, Exception) as e:
            logger.error(f"❌ Analysis failed, using fallback: {e}")
            state["analysis"] = {
                "severity_level": "medium",
                "category": "general",
                "sentiment_score": 0.0,
                "escalation_required": False,
                "key_issues": ["Unclassified issue"],
                "summary_reasoning": "Automatic fallback due to analysis failure"
            }

        return state


    def action_planning_agent(state: ComplaintState) -> ComplaintState:
        logger.info("⚙️ Action Planning Agent running")

        analysis = state.get("analysis", {})

        prompt = f"""Create action plan. Return ONLY this JSON:

    {{
    "internal_actions": [
        {{"action": "brief action", "responsible": "role", "priority": "high"}}
    ],
    "assigned_department": "department name",
    "estimated_resolution_time": "time"
    }}

    Severity: {analysis.get('severity_level')}
    Issues: {', '.join(analysis.get('key_issues', []))}

    JSON:"""

        try:
            result = llm.invoke(prompt)
            data = safe_json_load(result.content)
            
            # CRITICAL FIX: Ensure all required fields are present
            if "assigned_department" not in data:
                logger.warning("Missing 'assigned_department', adding default")
                data["assigned_department"] = "Front Desk"
            if "estimated_resolution_time" not in data:
                logger.warning("Missing 'estimated_resolution_time', adding default")
                data["estimated_resolution_time"] = "2 hours"
            if "internal_actions" not in data or not data["internal_actions"]:
                logger.warning("Missing or empty 'internal_actions', adding default")
                data["internal_actions"] = [{
                    "action": "Review and address complaint",
                    "responsible": "Department Manager",
                    "priority": "high"
                }]
            
            validated = ActionPlanOutput(**data)
            state["actions"] = validated.model_dump()
            logger.info(f"✅ Actions planned: {len(state['actions']['internal_actions'])} actions")
        except (ValidationError, Exception) as e:
            logger.error(f"❌ Action planning failed, using fallback: {e}")
            state["actions"] = {
                "internal_actions": [
                    {
                        "action": "Review complaint and contact guest",
                        "responsible": "Front Desk Manager",
                        "priority": "high"
                    }
                ],
                "assigned_department": "Front Desk",
                "estimated_resolution_time": "2 hours"
            }

        return state


    def response_agent(state: ComplaintState) -> ComplaintState:
        logger.info("✉️ Guest Response Agent running")

        analysis = state.get("analysis", {})
        actions = state.get("actions", {})

        # Build action summary
        action_list = actions.get("internal_actions", [])
        action_text = "\n".join([f"- {a.get('action', '')}" for a in action_list[:3]])

        prompt = f"""
    You are a professional hotel guest relations manager.

    Draft a polite, empathetic response to the guest.

    Guidelines:
    - Start with sincere apology if required
    - Show empathy
    - Mention specific actions being taken
    - Provide timeline: {actions.get('estimated_resolution_time', 'soon')}
    - Keep it professional but warm
    - 100-150 words
    - Do NOT mention: severity levels, scores, internal systems

    Guest Name: {state['guest_name']}
    Room: {state['room_number']}

    Their Complaint:
    {state['complaint_text']}

    Actions Being Taken:
    {action_text}

    Department: {actions.get('assigned_department', 'our team')}

    Write the response now.
    """

        try:
            result = llm.invoke(prompt)
            # Response agent doesn't need JSON, just text
            response_text = result.content.strip()
            
            # Remove any markdown formatting
            if response_text.startswith("```"):
                parts = response_text.split("```")
                response_text = parts[1] if len(parts) > 1 else response_text
                response_text = response_text.strip()
            
            state["response"] = {"guest_response": response_text}
            logger.info(f"✅ Response drafted: {len(response_text)} chars")
        except Exception as e:
            logger.error(f"❌ Response drafting failed: {e}")
            state["response"] = {
                "guest_response": f"Dear {state['guest_name']},\n\nWe sincerely apologize for the inconvenience you experienced. Our team is addressing this matter immediately and will resolve it within {actions.get('estimated_resolution_time', 'the shortest time possible')}.\n\nBest regards,\nGuest Relations Team"
            }

        return state


    def storage_agent(state: ComplaintState) -> ComplaintState:
        logger.info("💾 Storage Agent running")

        try:
            conn = sqlite3.connect("complaints.db", check_same_thread=False)
            cur = conn.cursor()

            # FIXED: Complete schema with all fields
            cur.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                complaint_id TEXT PRIMARY KEY,
                guest_name TEXT,
                room_number TEXT,
                contact_info TEXT,
                complaint_text TEXT,
                severity_level TEXT,
                category TEXT,
                sentiment_score REAL,
                escalation_required INTEGER,
                key_issues TEXT,
                summary_reasoning TEXT,
                internal_actions TEXT,
                assigned_department TEXT,
                estimated_resolution_time TEXT,
                guest_response TEXT,
                stored_successfully INTEGER,
                created_at TEXT
            )
            """)

            # Extract data safely
            analysis = state.get("analysis", {})
            actions = state.get("actions", {})
            response = state.get("response", {})

            # FIXED: Insert all 17 values
            cur.execute("""
            INSERT OR REPLACE INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state["complaint_id"],
                state["guest_name"],
                state["room_number"],
                state["contact_info"],
                state["complaint_text"],
                analysis.get("severity_level", "unknown"),
                analysis.get("category", "general"),
                analysis.get("sentiment_score", 0.0),
                int(analysis.get("escalation_required", False)),
                json.dumps(analysis.get("key_issues", [])),
                analysis.get("summary_reasoning", ""),
                json.dumps(actions.get("internal_actions", [])),
                actions.get("assigned_department", "Front Desk"),
                actions.get("estimated_resolution_time", "Unknown"),
                response.get("guest_response", ""),
                1,  # stored_successfully
                datetime.utcnow().isoformat()
            ))

            conn.commit()
            conn.close()

            state["stored_successfully"] = True
            state["notification_sent"] = analysis.get("escalation_required", False)
            logger.info(f"✅ Stored complaint: {state['complaint_id']}")

        except Exception as e:
            logger.error(f"❌ Storage failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            state["stored_successfully"] = False
            state["notification_sent"] = False

        return state


    # ------------------------------------------------------------------------------
    # Graph
    # ------------------------------------------------------------------------------
    def build_graph():
        graph = StateGraph(ComplaintState)

        graph.add_node("analyze", analysis_agent)
        graph.add_node("plan_actions", action_planning_agent)
        graph.add_node("draft_response", response_agent)
        graph.add_node("store", storage_agent)

        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "plan_actions")
        graph.add_edge("plan_actions", "draft_response")
        graph.add_edge("draft_response", "store")
        graph.add_edge("store", END)

        return graph.compile()


    GRAPH = build_graph()


    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------
    def process_complaint(
        complaint_text: str,
        guest_name: str,
        room_number: str,
        contact_info: str
    ) -> Dict[str, Any]:
        """Process a hotel complaint through the 3-agent system"""

        state: ComplaintState = {
            "complaint_id": str(uuid.uuid4()),
            "guest_name": guest_name,
            "room_number": room_number,
            "contact_info": contact_info,
            "complaint_text": complaint_text,
            "analysis": {},
            "actions": {},
            "response": {},
            "stored_successfully": False,
            "notification_sent": False,
        }

        final_state = GRAPH.invoke(state)

        # Merge all results into flat dict
        return {
            **final_state,
            **final_state.get("analysis", {}),
            **final_state.get("actions", {}),
            **final_state.get("response", {}),
        }