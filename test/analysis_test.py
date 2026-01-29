import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.analysis_agent import analysis_agent



def main():
    
    complaint_state = {
        "guest_name": "Rahul Mehta",
        "room_number": "312",
        "contact_info": "rahul.mehta@email.com",
        "complaint_text": (
            "The air conditioner stopped working at night. "
            "I called the front desk twice but no one responded. "
            "The room became unbearable."
        )
    }

    print("\n=== TEST CASE 1: COMPLAINT ===")
    result = analysis_agent(complaint_state)
    print(result["analysis"])


    # Test Case 2: Positive Feedback
    feedback_state = {
        "guest_name": "Neha Sharma",
        "room_number": "508",
        "contact_info": "neha.sharma@email.com",
        "complaint_text": (
            "I had a wonderful stay. The staff was polite and "
            "the room was always clean. Great experience!"
        )
    }

    print("\n=== TEST CASE 2: FEEDBACK ===")
    result = analysis_agent(feedback_state)
    print(result["analysis"])


if __name__ == "__main__":
    main()
