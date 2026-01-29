"""
Response Agent - Drafts professional, empathetic guest communications
Uses guidance from action planning agent to craft appropriate responses
"""
import logging

from langchain_ollama import ChatOllama

from app.schema import ComplaintState
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    num_predict=settings.LLM_MAX_TOKENS,
)

def response_agent(state: ComplaintState) -> ComplaintState:
    """Draft professional guest response"""
    logger.info("✉️ Response Agent running")

    # Extract context
    analysis = state.get("shared_memory", {}).get("analysis", {})
    actions = state.get("shared_memory", {}).get("actions", {})
    
    severity = analysis.get("severity_level", "medium")
    category = analysis.get("category", "general")
    sentiment_score = analysis.get("sentiment_score", 0.0)
    
    # Get guidance from action planner
    response_tone = actions.get("guest_response_tone", "professional and empathetic")
    response_focus = actions.get("response_focus", [])
    compensation = actions.get("compensation_recommended")
    estimated_time = actions.get("estimated_resolution_time", "soon")
    department = actions.get("assigned_department", "our team")
    
    # Determine if positive feedback
    is_positive_feedback = (sentiment_score > 0.5 and category == "positive_feedback")
    
    # Build prompt
    if is_positive_feedback:
        prompt = f"""Write a warm thank-you response to positive hotel feedback.

Guest: {state.get('guest_name')}
Feedback: "{state.get('complaint_text')}"

Guidelines:
- Express sincere gratitude
- Acknowledge specific positives
- Invite them back
- 100-150 words
- NO apologies (nothing to apologize for!)

Response:"""
    else:
        prompt = f"""Write a professional apology and resolution response.

Guest: {state.get('guest_name')} (Room {state.get('room_number')})
Complaint: "{state.get('complaint_text')}"

Severity: {severity}
Department: {department}
Timeline: {estimated_time}
Compensation: {compensation if compensation else 'None'}

Guidelines:
- Apologize sincerely
- Explain actions being taken
- Provide timeline
- {f'Offer: {compensation}' if compensation else ''}
- 150-200 words

Response:"""

    try:
        result = llm.invoke(prompt)
        response_text = result.content.strip()
        
        # Clean markdown
        if response_text.startswith("```"):
            parts = response_text.split("```")
            response_text = parts[1] if len(parts) > 1 else response_text
            response_text = response_text.strip()
        
        if len(response_text) < 50:
            raise ValueError("Response too short")
        
        # ✅ CRITICAL FIX: Write to BOTH shared_memory AND direct field
        response_data = {
            "guest_response": response_text,
            "response_type": "positive_feedback" if is_positive_feedback else "complaint"
        }
        
        # Write to shared_memory (primary)
        state["shared_memory"]["response"] = response_data
        
        # Write to direct field (backup/compatibility)
        state["response"] = response_data
        
        logger.info(f"✅ Response drafted: {len(response_text)} chars")
        
    except Exception as e:
        logger.error(f"❌ Response failed: {e}")
        
        # Fallback
        if is_positive_feedback:
            fallback = f"Dear {state.get('guest_name')},\n\nThank you for your wonderful feedback! We're delighted you enjoyed your stay. We look forward to welcoming you back!\n\nWarm regards,\nGuest Relations"
        else:
            fallback = f"Dear {state.get('guest_name')},\n\nWe apologize for the inconvenience. Our {department} is addressing this and will resolve it within {estimated_time}.\n\nBest regards,\nGuest Relations"
        
        fallback_data = {
            "guest_response": fallback,
            "response_type": "fallback"
        }
        
        # ✅ Write to BOTH
        state["shared_memory"]["response"] = fallback_data
        state["response"] = fallback_data
        
        logger.warning("Using fallback response")

    return state