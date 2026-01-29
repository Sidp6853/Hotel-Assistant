from agent import process_complaint
import json

def save_result_as_json(result, filename="complaint_output.json"):
    """Save the full complaint/result as a JSON file"""
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Saved full complaint to {filename}")



def run_demo():
    print("\n================ HOTEL AI SUPPORT AGENT DEMO ================\n")

    complaint_case = {
        "guest_name": "Rahul Mehta",
        "room_number": "312",
        "contact_info": "rahul.mehta@email.com",
        "complaint_text": (
            "The air conditioner in my room stopped working late at night. "
            "I called the front desk twice but no one came to fix it. "
            "It was extremely uncomfortable and I couldn’t sleep properly."
        )
    }

    print("🔴 CASE 1:\n")

    result_complaint = process_complaint(**complaint_case)

    print("Final Output:")
    print(json.dumps(result_complaint, indent=2))

    save_result_as_json(result_complaint, "case_1.json") 

    feedback_case = {
        "guest_name": "Neha Sharma",
        "room_number": "508",
        "contact_info": "neha.sharma@email.com",
        "complaint_text": (
            "I had a wonderful stay. The check-in process was quick, "
            "the staff was very polite, and the room was clean throughout my stay. "
            "Special thanks to the housekeeping team."
        )
    }

    print("\n\n🟢 CASE 2\n")

    result_feedback = process_complaint(**feedback_case)

    print("Final Output:")
    print(json.dumps(result_feedback, indent=2))

    save_result_as_json(result_feedback, "case_2.json")  # ← added


if __name__ == "__main__":
    run_demo()
