"""
Demo script for Hotel Complaint Management System
Tests 4 scenarios covering all severity levels
"""

from complaint_agent import process_complaint
import json
from datetime import datetime


def save_result(result: dict, scenario_num: int):
    """Save result to JSON file"""
    filename = f"output_scenario_{scenario_num}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Saved to: {filename}")


def print_result(result: dict):
    """Print formatted result"""
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    
    print(f"\n🆔 Complaint ID: {result['complaint_id']}")
    print(f"👤 Guest: {result['guest_name']} (Room {result['room_number']})")
    
    print(f"\n📈 ANALYSIS:")
    print(f"   • Severity: {result['severity_level'].upper()}")
    print(f"   • Category: {result['category']}")
    print(f"   • Sentiment: {result['sentiment_score']:.2f}")
    print(f"   • Escalation: {'YES' if result['escalation_required'] else 'NO'}")
    
    print(f"\n💭 REASONING (Chain-of-Thought):")
    reasoning = result.get('reasoning_steps', '')
    if len(reasoning) > 300:
        print(f"   {reasoning[:300]}...")
    else:
        print(f"   {reasoning}")
    
    print(f"\n🔍 KEY ISSUES:")
    for issue in result.get('key_issues', []):
        print(f"   • {issue}")
    
    print(f"\n⚙️  INTERNAL ACTIONS:")
    for i, action in enumerate(result.get('internal_actions', []), 1):
        print(f"   {i}. [{action.get('priority', 'normal').upper()}] {action.get('action', '')}")
        print(f"      → {action.get('responsible', 'Unknown')}")
    
    print(f"\n📍 ROUTING:")
    print(f"   • Department: {result.get('assigned_department', 'Unknown')}")
    print(f"   • Resolution Time: {result.get('estimated_resolution_time', 'Unknown')}")
    
    print(f"\n✉️  GUEST RESPONSE:")
    print("-"*80)
    print(result.get('guest_response', 'No response'))
    print("-"*80)
    
    print(f"\n💾 STORAGE:")
    print(f"   • Stored: {'YES' if result.get('stored_successfully') else 'NO'}")
    print(f"   • Notification: {'YES' if result.get('notification_sent') else 'NO'}")


def run_demo():
    """Run all demo scenarios"""
    
    scenarios = [
        {
            "name": "CRITICAL - Health & Safety Emergency",
            "complaint": """This is urgent! I found a cockroach in my room (#512) and there 
            are several dead insects near the bathroom. My daughter has severe allergies and 
            we cannot stay in this room. We need immediate relocation and I'm considering 
            contacting health authorities. This is a serious health and safety violation.""",
            "guest_name": "Sarah Johnson",
            "room_number": "512",
            "contact_info": "sarah.j@email.com"
        },
        {
            "name": "HIGH - Major Service Failure",
            "complaint": """I checked in 3 hours ago and STILL haven't received my luggage 
            from the bell desk. I've called FOUR times and keep getting told "it's coming soon". 
            I have important business meetings in 2 hours and need my clothes and presentation 
            materials. This level of service is completely unacceptable and unprofessional.""",
            "guest_name": "Michael Chen",
            "room_number": "208",
            "contact_info": "m.chen@business.com"
        },
        {
            "name": "MEDIUM - Room Maintenance Issues",
            "complaint": """The room has several issues that need attention - the TV remote 
            doesn't work at all, there's a strange musty smell coming from the AC vent, and 
            the shower drain is very slow. It's not terrible but definitely not what I expected 
            from your hotel. Please send someone to fix these issues today.""",
            "guest_name": "Emily Rodriguez",
            "room_number": "103",
            "contact_info": "emily.r@gmail.com"
        },
        {
            "name": "LOW - Amenity Request",
            "complaint": """Hi there! I just checked in and noticed there are no coffee pods 
            in the room, and there's only one pillow on the bed (I prefer two). Also, it would 
            be great to have some extra towels. Not urgent but would appreciate if someone 
            could bring these items when convenient. Thank you!""",
            "guest_name": "David Park",
            "room_number": "425",
            "contact_info": "d.park@email.com"
        }
    ]
    
    print("\n" + "🎬"*40)
    print("HOTEL COMPLAINT SYSTEM - DEMO")
    print("🎬"*40)
    print(f"\nRunning {len(scenarios)} test scenarios...")
    print("This will take ~2-3 minutes with llama3.2:3b")
    print("\n" + "="*80)
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'#'*80}")
        print(f"SCENARIO {i}/{len(scenarios)}: {scenario['name']}")
        print('#'*80)
        print(f"\nComplaint Preview:")
        print(f"   {scenario['complaint'][:150]}...")
        print()
        
        try:
            result = process_complaint(
                complaint_text=scenario['complaint'],
                guest_name=scenario['guest_name'],
                room_number=scenario['room_number'],
                contact_info=scenario['contact_info']
            )
            
            print_result(result)
            save_result(result, i)
            results.append(result)
            
        except Exception as e:
            print(f"\n❌ ERROR in scenario {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Summary
    print("\n\n" + "="*80)
    print("📈 DEMO SUMMARY")
    print("="*80)
    
    print(f"\nCompleted: {len(results)}/{len(scenarios)} scenarios")
    
    if results:
        severity_counts = {}
        for result in results:
            sev = result.get('severity_level', 'unknown')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print(f"\nSeverity Distribution:")
        for severity, count in sorted(severity_counts.items()):
            print(f"   • {severity.capitalize()}: {count}")
        
        escalations = sum(1 for r in results if r.get('escalation_required'))
        print(f"\nEscalations: {escalations}")
        
        stored = sum(1 for r in results if r.get('stored_successfully'))
        print(f"Stored in DB: {stored}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\nCheck output_scenario_*.json for full results")
    print("Check complaints.db for database records")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🏨  HOTEL COMPLAINT MANAGEMENT SYSTEM - DEMO                ║
║                                                                ║
║   3-Agent AI System with Chain-of-Thought Reasoning           ║
║   Built with LangGraph + Ollama (Local LLM)                   ║
║                                                                ║
║   Architecture: Analysis → Actions → Response → Storage       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    
    print("Waiting for input...")
    input()

    
    run_demo()