"""
Main entry point for Hotel Complaint Management System
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Path setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports
from config.settings import settings
from app.tools.rag_tool import policy_rag
from app.tools.database import initialize_database
from app.graph.workflow import process_complaint  # ✅ Check your actual path

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def initialize_system() -> bool:
    """Initialize system components"""
    try:
        logger.info("=" * 80)
        logger.info("🏨 INITIALIZING HOTEL COMPLAINT MANAGEMENT SYSTEM")
        logger.info("=" * 80)

        logger.info("💾 Initializing database...")
        initialize_database()
        logger.info(f"✅ Database ready at {settings.DB_PATH}")

        if settings.RAG_ENABLED:
            logger.info("📚 Initializing RAG system...")
            policy_rag.initialize()
            logger.info("✅ RAG system ready")

        logger.info("⚙️ Configuration:")
        logger.info(f"   • LLM Model: {settings.LLM_MODEL}")
        logger.info(f"   • Temperature: {settings.LLM_TEMPERATURE}")
        logger.info(f"   • Max Tokens: {settings.LLM_MAX_TOKENS}")
        logger.info(f"   • Database: {settings.DB_PATH}")
        logger.info(f"   • RAG Enabled: {settings.RAG_ENABLED}")
        logger.info("=" * 80)
        logger.info("✅ SYSTEM INITIALIZATION COMPLETE")
        logger.info("=" * 80 + "\n")
        return True

    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        logger.exception("Full traceback:")
        return False


def prompt_user_input() -> dict:
    """Prompt user for complaint details"""
    print("\n📝 PLEASE ENTER COMPLAINT DETAILS")
    print("-" * 60)

    complaint_text = input("📢 Complaint description:\n> ").strip()
    guest_name = input("👤 Guest name: ").strip()
    room_number = input("🏨 Room number: ").strip()
    contact_info = input("📧 Contact info (email/phone): ").strip()

    return {
        "complaint_text": complaint_text,
        "guest_name": guest_name,
        "room_number": room_number,
        "contact_info": contact_info,
    }


def save_result_to_json(result: dict, guest_name: str) -> str:
    """Save result to individual JSON file"""
    try:
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = guest_name.replace(" ", "_")[:20]
        filename = output_dir / f"complaint_{safe_name}_{timestamp}.json"
        
        # Save JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Individual result saved to: {filename}")
        return str(filename)
        
    except Exception as e:
        logger.error(f"❌ Failed to save JSON: {e}")
        return None


def display_result(result: dict):
    """Display processing results"""
    analysis = result.get("analysis", {})
    actions = result.get("actions", {})
    response = result.get("response", {})

    print("\n" + "=" * 80)
    print("📋 COMPLAINT ANALYSIS")
    print("=" * 80)
    print(f"Severity        : {analysis.get('severity_level', 'unknown').upper()}")
    print(f"Category        : {analysis.get('category', 'unknown')}")
    print(f"Sentiment Score : {analysis.get('sentiment_score', 0.0):.2f}")
    print(f"Escalation      : {'YES' if analysis.get('escalation_required') else 'NO'}")

    print("\n" + "=" * 80)
    print("⚙️ ACTION PLAN")
    print("=" * 80)
    print(f"Department      : {actions.get('assigned_department', 'N/A')}")
    print(f"ETA             : {actions.get('estimated_resolution_time', 'N/A')}")
    print(f"Compensation    : {actions.get('compensation_recommended', 'None')}")

    print("\n🛠 Internal Actions:")
    for i, act in enumerate(actions.get("internal_actions", []), 1):
        action_text = act.get('action', 'No action')
        # Truncate if too long
        if len(action_text) > 100:
            action_text = action_text[:97] + "..."
        print(f"  {i}. {action_text}")
        print(f"     → Responsible: {act.get('responsible', 'N/A')}")
        print(f"     → Priority   : {act.get('priority', 'normal')}")
        print(f"     → Timeline   : {act.get('timeline', 'ASAP')}")

    print("\n" + "=" * 80)
    print("📧 GUEST RESPONSE")
    print("=" * 80)
    
    # ✅ CRITICAL FIX: Check all possible locations
    guest_response = (
        result.get("guest_response") or
        response.get("guest_response") or
        result.get("response", {}).get("guest_response") or
        "⚠️ No response generated"
    )
    
    print(guest_response)
    print("=" * 80 + "\n")


def main():
    """Main function"""
    logger.info("🏨 HOTEL COMPLAINT MANAGEMENT SYSTEM STARTING\n")

    if not initialize_system():
        logger.error("❌ System failed to initialize. Exiting...")
        return

    while True:
        user_input = prompt_user_input()

        try:
            # Process complaint
            result = process_complaint(**user_input)
            
            # Display results
            display_result(result)
            
            # ✅ Save to individual JSON file
            json_file = save_result_to_json(result, user_input['guest_name'])
            if json_file:
                print(f"📁 Individual result saved to: {json_file}")
            
            # Show history location
            print(f"📚 All complaints saved to: data/complaints_history.json\n")

        except Exception as e:
            logger.error(f"❌ Complaint processing failed: {e}")
            logger.exception("Full traceback:")

        choice = input("🔁 Submit another complaint? (y/n): ").strip().lower()
        if choice not in ("y", "yes"):
            print("\n👋 Thank you for using the Hotel Complaint Management System!")
            break


if __name__ == "__main__":
    main()