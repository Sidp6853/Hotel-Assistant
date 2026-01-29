"""
Complete Workflow - Orchestrates all agents using LangGraph
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from langgraph.graph import StateGraph, END

from app.schema import ComplaintState
from app.agents.analysis_agent import analysis_agent
from app.agents.action_planning_agent import action_planning_agent
from app.agents.response_agent import response_agent

logger = logging.getLogger(__name__)


def build_workflow() -> StateGraph:
    """Build the complaint processing workflow"""
    logger.info("Building complaint processing workflow...")
    
    workflow = StateGraph(ComplaintState)
    
    workflow.add_node("analyze", analysis_agent)
    workflow.add_node("plan_actions", action_planning_agent)
    workflow.add_node("draft_response", response_agent)
    
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "plan_actions")
    workflow.add_edge("plan_actions", "draft_response")
    workflow.add_edge("draft_response", END)
    
    logger.info("✅ Workflow built successfully")
    
    return workflow.compile()


WORKFLOW = build_workflow()


def store_complaint_history(record: dict):
    """Save complaint to history"""
    try:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        file_path = data_dir / "complaints_history.json"

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        record["processed_at"] = datetime.now().isoformat()
        existing.append(record)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved to history: {file_path}")
    except Exception as e:
        logger.error(f"❌ History save failed: {e}")


def process_complaint(
    complaint_text: str,
    guest_name: str,
    room_number: str,
    contact_info: str
) -> Dict[str, Any]:
    """Process complaint through workflow"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🏨 PROCESSING COMPLAINT")
    logger.info(f"{'='*80}")
    logger.info(f"Guest: {guest_name} (Room {room_number})")
    logger.info(f"Contact: {contact_info}")
    logger.info(f"{'='*80}")
    
    # ✅ Create initial state WITH shared_memory
    initial_state: ComplaintState = {
        "guest_name": guest_name,
        "room_number": room_number,
        "contact_info": contact_info,
        "complaint_text": complaint_text,
        
        # ✅ shared_memory for agents to write to
        "shared_memory": {
            "analysis": {},
            "actions": {},
            "response": {},
            "metadata": {}
        },
        
        # Keep these for compatibility
        "analysis": {},
        "actions": {},
        "response": {},
        
        "stored_successfully": False,
        "notification_sent": False
    }

    try:
        logger.info("🚀 Starting workflow execution...")
        final_state = WORKFLOW.invoke(initial_state)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ WORKFLOW COMPLETED")
        logger.info(f"{'='*80}")
        
        # ✅ Extract from shared_memory
        shared = final_state.get("shared_memory", {})
        analysis = shared.get("analysis", {})
        actions = shared.get("actions", {})
        response = shared.get("response", {})
        
        # Build result with FLATTENED fields for easy access
        result = {
            # Input
            "guest_name": final_state.get("guest_name"),
            "room_number": final_state.get("room_number"),
            "contact_info": final_state.get("contact_info"),
            "complaint_text": final_state.get("complaint_text"),
            
            # Nested (for structure)
            "analysis": analysis,
            "actions": actions,
            "response": response,
            
            # ✅ FLATTENED (for easy access in main.py)
            "severity_level": analysis.get("severity_level"),
            "category": analysis.get("category"),
            "sentiment_score": analysis.get("sentiment_score"),
            "escalation_required": analysis.get("escalation_required"),
            "key_issues": analysis.get("key_issues", []),
            "summary_reasoning": analysis.get("summary_reasoning"),
            
            "internal_actions": actions.get("internal_actions", []),
            "assigned_department": actions.get("assigned_department"),
            "estimated_resolution_time": actions.get("estimated_resolution_time"),
            "compensation_recommended": actions.get("compensation_recommended"),
            "guest_response_tone": actions.get("guest_response_tone"),
            "response_focus": actions.get("response_focus", []),
            
            "guest_response": response.get("guest_response"),  # ✅ KEY
            "response_type": response.get("response_type"),
            
            "stored_successfully": final_state.get("stored_successfully", False),
            "notification_sent": final_state.get("notification_sent", False),
        }
        
        # Log summary
        logger.info(f"📊 SUMMARY:")
        logger.info(f"   • Severity: {result.get('severity_level', 'unknown').upper()}")
        logger.info(f"   • Category: {result.get('category', 'unknown')}")
        logger.info(f"   • Sentiment: {result.get('sentiment_score', 0.0):.2f}")
        logger.info(f"   • Escalation: {'YES' if result.get('escalation_required') else 'NO'}")
        logger.info(f"   • Department: {result.get('assigned_department', 'unknown')}")
        logger.info(f"{'='*80}\n")
        
        # Save to history
        store_complaint_history(result)
        
        return result
        
    except Exception as e:
        logger.error(f"\n{'='*80}")
        logger.error(f"❌ WORKFLOW FAILED")
        logger.error(f"{'='*80}")
        logger.error(f"Error: {str(e)}")
        logger.exception("Full traceback:")
        
        return {
            "guest_name": guest_name,
            "room_number": room_number,
            "error": str(e),
            "workflow_failed": True,
        }