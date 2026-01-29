"""
Manual test for Action Planning Agent with better error handling
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.action_planning_agent import action_planning_agent
from app.tools.rag_tool import policy_rag


def print_action_plan(result, case_name):
    """Pretty print action plan with error handling"""
    try:
        actions = result.get('actions', {})
        
        print(f"\n--- ACTION PLAN FOR {case_name} ---")
        print(f"Department: {actions.get('assigned_department', 'N/A')}")
        print(f"Timeline: {actions.get('estimated_resolution_time', 'N/A')}")
        print(f"Compensation: {actions.get('compensation_recommended', 'None')}")
        print(f"Tone: {actions.get('guest_response_tone', 'N/A')}")
        
        internal_actions = actions.get('internal_actions', [])
        print(f"\nActions ({len(internal_actions)}):")
        for i, action in enumerate(internal_actions, 1):
            action_text = action.get('action', 'N/A')
            print(f"  {i}. {action_text[:80]}...")
        
        print(f"\nResponse Focus: {actions.get('response_focus', [])}")
        print()
        
    except Exception as e:
        print(f"❌ Error printing action plan: {e}")
        print(f"Raw result: {json.dumps(result, indent=2)}")


def main():
    # Initialize RAG once
    print("Initializing RAG...")
    policy_rag.initialize()
    print()

    # =========================================================================
    # TEST CASE 1: HIGH SEVERITY COMPLAINT
    # =========================================================================
    print("="*70)
    print("TEST CASE 1: HIGH SEVERITY - AC MALFUNCTION")
    print("="*70)
    
    complaint_state = {
        "complaint_id": "test-001",
        "guest_name": "Rahul Mehta",
        "room_number": "504",
        "contact_info": "rahul.mehta@email.com",
        "complaint_text": (
            "The AC in my room stopped working late last night. "
            "I called the front desk twice but nobody showed up. "
            "The room was extremely uncomfortable and I couldn't sleep."
        ),
        "analysis": {
            "severity_level": "high",
            "category": "maintenance",
            "sentiment_score": -0.8,
            "escalation_required": True,
            "key_issues": [
                "Air conditioner not working",
                "No response from front desk"
            ],
            "summary_reasoning": "Critical failure with inadequate staff response"
        },
        "actions": {},
        "response": {},
        "recurring_guest": False,
        "recurring_room_issue": False,
        "stored_successfully": False,
        "notification_sent": False
    }

    try:
        print("Processing Test Case 1...")
        result_1 = action_planning_agent(complaint_state)
        print_action_plan(result_1, "TEST CASE 1")
    except Exception as e:
        print(f"❌ Test Case 1 failed: {e}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # TEST CASE 2: POSITIVE FEEDBACK
    # =========================================================================
    print("="*70)
    print("TEST CASE 2: LOW SEVERITY - POSITIVE FEEDBACK")
    print("="*70)
    
    feedback_state = {
        "complaint_id": "test-002",
        "guest_name": "Ananya Sharma",
        "room_number": "312",
        "contact_info": "ananya.sharma@email.com",
        "complaint_text": (
            "I really enjoyed my stay. The staff was polite and helpful, "
            "and the room was very clean. Keep up the good work!"
        ),
        "analysis": {
            "severity_level": "low",
            "category": "positive_feedback",
            "sentiment_score": 0.75,
            "escalation_required": False,
            "key_issues": ["Positive staff feedback", "Room cleanliness praised"],  # Fixed!
            "summary_reasoning": "Guest expressed high satisfaction"
        },
        "actions": {},
        "response": {},
        "recurring_guest": False,
        "recurring_room_issue": False,
        "stored_successfully": False,
        "notification_sent": False
    }

    try:
        print("Processing Test Case 2...")
        result_2 = action_planning_agent(feedback_state)
        print_action_plan(result_2, "TEST CASE 2")
    except Exception as e:
        print(f"❌ Test Case 2 failed: {e}")
        import traceback
        traceback.print_exc()

    print("="*70)
    print("✅ All tests completed")
    print("="*70)


if __name__ == "__main__":
    main()