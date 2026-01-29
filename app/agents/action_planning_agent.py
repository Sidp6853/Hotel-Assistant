"""
Action Planning Agent - Creates internal action plans and provides response guidance
Uses RAG to retrieve relevant hotel policies for accurate action planning
"""
import logging
from typing import Optional
from pydantic import ValidationError

from langchain_ollama import ChatOllama

from app.schema import ComplaintState, ActionPlanOutput, ActionItem
from app.utils.json_parser import safe_json_load
from app.tools.rag_tool import policy_rag
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    num_predict=settings.LLM_MAX_TOKENS,
)


def action_planning_agent(state: ComplaintState) -> ComplaintState:
    logger.info("⚙️ Action Planning Agent running")

    # ✅ NEW: Read from shared_memory
    analysis = state.get("shared_memory", {}).get("analysis", {})
    
    # If shared_memory is empty, fall back to direct state (backward compatibility)
    if not analysis:
        analysis = state.get("analysis", {})
    
    severity = analysis.get("severity_level", "medium")
    category = analysis.get("category", "general")
    key_issues = analysis.get("key_issues", [])
    sentiment_score = analysis.get("sentiment_score", 0.0)
    
    
    
    # STEP 1: Retrieve relevant policies using RAG
    logger.info(f"🔍 Querying RAG for policies (Category: {category}, Severity: {severity})")
    
    # Build RAG query from complaint context
    rag_query = f"{category} {severity} severity complaint resolution: {' '.join(key_issues)}"
    relevant_policies = policy_rag.retrieve(rag_query, k=3)
    
    if relevant_policies:
        policy_context = "\n\n".join([f"Policy {i+1}: {policy}" 
                                      for i, policy in enumerate(relevant_policies)])
        logger.info(f"✅ Retrieved {len(relevant_policies)} relevant policies")
    else:
        policy_context = "No specific policies found. Use standard hotel service recovery best practices."
        logger.warning("⚠️ No policies retrieved from RAG")

    # STEP 2: Build comprehensive prompt for LLM (NO STATIC RULES)
    prompt = f"""You are an experienced hotel operations manager creating an action plan to resolve a guest complaint.

GUEST INFORMATION:
- Name: {state.get('guest_name')}
- Room: {state.get('room_number')}
- Contact: {state.get('contact_info')}

ORIGINAL COMPLAINT:
\"\"\"{state.get('complaint_text')}\"\"\"

ANALYSIS RESULTS:
- Severity: {severity}
- Category: {category}
- Key Issues: {', '.join(key_issues)}
- Sentiment Score: {sentiment_score:.2f} (range: -1.0 to 1.0)
- Escalation Required: {analysis.get('escalation_required', False)}

HOTEL POLICIES & GUIDELINES:
{policy_context}

YOUR TASK:
Create a comprehensive internal action plan that includes:

1. **Immediate Actions** (within 15-30 mins):
   - Guest acknowledgment and apology
   - Initial response steps

2. **Resolution Actions** (30 mins - 2 hours):
   - Fix the actual problem
   - Assign specific departments/roles
   - Set realistic timelines

3. **Follow-up Actions** (if severity is high/critical):
   - Verify guest satisfaction
   - Document for future prevention

4. **Compensation Recommendation**:
   - Based on severity, impact, and hotel policies
   - Consider: Room upgrades, discounts, complimentary services, refunds
   - If severity is low or positive feedback, compensation may not be needed
   - Be realistic and proportionate to the issue

5. **Response Guidance for Guest Communication**:
   - Recommended tone (apologetic, empathetic, professional, warm, etc.)
   - Key points to emphasize (NOT the full response text, just guidance)
   - Example: ["Immediate action being taken", "Timeline commitment", "Compensation offer"]
   - DO NOT write the actual response - that's the next agent's job

SPECIAL CASES:

**If this is POSITIVE FEEDBACK (sentiment > 0.5, category = "positive_feedback"):**
- Set compensation_recommended to null (no compensation for positive feedback)
- Tone should be "warm and appreciative" NOT "apologetic"
- Actions should be: Thank guest, share feedback with staff, invite return
- Response focus: "Express gratitude", "Acknowledge staff", "Encourage return visit"
- DO NOT apologize or mention "resolving issues" - there is no issue!

**If this is a COMPLAINT (sentiment < 0):**
- Follow standard complaint resolution procedures
- Consider compensation based on severity
- Tone should be apologetic/empathetic

IMPORTANT GUIDELINES:
- Be SPECIFIC: Include room numbers, department names, exact timelines
- Be REALISTIC: Don't promise what can't be delivered
- Follow HOTEL POLICIES: Use the retrieved policies as your guide
- Be PROPORTIONATE: Match compensation to severity and impact
- For positive feedback: Focus on gratitude, not compensation

Return ONLY valid JSON (no markdown, no explanations):

{{
  "internal_actions": [
    {{
      "action": "Specific, detailed action description",
      "responsible": "Department or Role name",
      "priority": "urgent|high|medium|low",
      "timeline": "Specific timeframe (e.g., Within 20 minutes)"
    }}
  ],
  "assigned_department": "Primary department(s) responsible",
  "estimated_resolution_time": "Realistic overall timeline",
  "compensation_recommended": "Specific compensation offer OR null if not needed",
  "guest_response_tone": "Tone description for response agent",
  "response_focus": ["Key point 1", "Key point 2", "Key point 3"]
}}

Requirements:
- 2-5 internal actions (based on complexity)
- All timelines must be realistic
- Compensation must follow hotel policies (from above)
- Response tone must match severity and sentiment

JSON:"""

    try:
        # STEP 3: Get action plan from LLM
        result = llm.invoke(prompt)
        data = safe_json_load(result.content)
        
        # STEP 4: Basic validation (minimal intervention)
        if "assigned_department" not in data or not data["assigned_department"]:
            data["assigned_department"] = "Guest Relations Department"
        
        if "estimated_resolution_time" not in data or not data["estimated_resolution_time"]:
            data["estimated_resolution_time"] = "Within 2 hours"
        
        if "internal_actions" not in data or not data["internal_actions"]:
            # Only fallback if completely missing
            data["internal_actions"] = [{
                "action": f"Review and address complaint in room {state.get('room_number')}",
                "responsible": "Guest Relations Manager",
                "priority": "high" if severity in ["high", "critical"] else "medium",
                "timeline": "Within 1 hour"
            }]
        
        if "guest_response_tone" not in data:
            data["guest_response_tone"] = "professional and empathetic"
        
        if "response_focus" not in data or not data["response_focus"]:
            data["response_focus"] = ["Acknowledge concern", "Provide resolution timeline"]
        
        # Validate with Pydantic
        validated = ActionPlanOutput(**data)
        actions_result = validated.model_dump()
        
        state["actions"] = actions_result  # Backward compatibility
        state["shared_memory"]["actions"] = actions_result  # Shared memory
        
        logger.info(
            f"✅ Action plan created: "
            f"{len(actions_result['internal_actions'])} actions, "
            f"Department: {actions_result['assigned_department']}, "
            f"Compensation: {actions_result.get('compensation_recommended', 'None')}"
        )
        
    except (ValidationError, Exception) as e:
        logger.error(f"❌ Action planning failed: {e}")
        logger.exception("Full traceback:")
        
        # Minimal fallback
        fallback_actions = {
            "internal_actions": [{
                "action": f"Contact guest and address complaint regarding {category}",
                "responsible": "Guest Relations Department",
                "priority": "high" if severity in ["high", "critical"] else "medium",
                "timeline": "Within 1 hour"
            }],
            "assigned_department": "Guest Relations Department",
            "estimated_resolution_time": "Within 2 hours",
            "compensation_recommended": None,
            "guest_response_tone": "professional and empathetic",
            "response_focus": ["Acknowledge issue", "Provide solution"]
        }
        
        # ✅ NEW: Update both
        state["actions"] = fallback_actions
        state["shared_memory"]["actions"] = fallback_actions
        
        logger.warning("⚠️ Using minimal fallback action plan")

    return state