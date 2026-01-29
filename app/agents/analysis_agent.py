import logging
from pydantic import ValidationError

from langchain_ollama import ChatOllama

from app.schema import ComplaintState, AnalysisOutput
from app.utils.json_parser import safe_json_load
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    num_predict=settings.LLM_MAX_TOKENS,
)


def analysis_agent(state: ComplaintState) -> ComplaintState:
    """
    Analyze complaint for severity, sentiment, and categorization
    
    Uses LLM reasoning with structured guidelines to classify complaints.
    Updates shared_memory with analysis results.
    
    Args:
        state: Current complaint state
        
    Returns:
        Updated state with analysis results in shared_memory
    """
    logger.info("🔍 Analysis Agent running")

    prompt = f"""You are an expert hotel complaint analysis system. Analyze the following guest complaint and classify it accurately.

SEVERITY LEVELS (choose the most appropriate):

1. **CRITICAL** - Immediate action required
   - Safety or health hazards (fire, injury, illness, pests)
   - Severe privacy violations or security breaches
   - Guest threatening immediate checkout or legal action
   - Multiple critical failures with no response from staff
   - Should escalate: YES

2. **HIGH** - Urgent attention needed
   - Essential amenities completely non-functional (AC, hot water, heating)
   - Repeated failures with inadequate staff response
   - Significant cleanliness issues (dirty room, stained bedding)
   - Major billing disputes
   - Guest expressing extreme dissatisfaction
   - Should escalate: YES

3. **MEDIUM** - Needs prompt attention
   - Single amenity malfunction (TV, WiFi, phone)
   - Noise disturbances
   - Minor maintenance issues
   - Service delays (housekeeping, front desk)
   - Room comfort issues (uncomfortable bed/pillows)
   - Should escalate: NO (unless recurring)

4. **LOW** - Standard handling
   - General inquiries or questions
   - Late check-in/check-out arrangements
   - Minor requests or preferences
   - Positive feedback with minor suggestions
   - Billing clarifications
   - Should escalate: NO

CATEGORIES (choose ONE that best fits):
- maintenance: AC, plumbing, electrical, heating issues
- cleanliness: Housekeeping, dirty room, sanitation
- amenities: TV, WiFi, facilities, smart devices
- service: Staff behavior, wait times, responsiveness
- billing: Charges, fees, payment issues
- noise: Disturbances, loud neighbors
- privacy: Unauthorized room entry, security concerns
- safety: Hazards, dangerous conditions
- food_beverage: Restaurant, room service issues
- parking: Parking fees, availability
- check_in_out: Front desk, reservation issues
- general: Miscellaneous or mixed issues
- positive_feedback: Compliments or praise

SENTIMENT SCORE GUIDELINES (-1.0 to 1.0):
Think about the emotional tone and language intensity:
- **-1.0 to -0.7**: Extremely angry, using strong negative language, threats, profanity
- **-0.6 to -0.4**: Very upset, expressing significant frustration or disappointment
- **-0.3 to -0.1**: Mildly negative, slightly disappointed or inconvenienced
- **0.0**: Neutral, factual reporting without emotional language
- **0.1 to 0.3**: Slightly positive, constructive feedback
- **0.4 to 0.6**: Positive, expressing satisfaction or appreciation
- **0.7 to 1.0**: Very positive, highly complimentary, exceptional praise

ESCALATION DECISION:
- Escalate if severity is HIGH or CRITICAL
- Escalate if guest mentions checking out early, posting reviews, or legal action
- Otherwise, standard handling is sufficient

COMPLAINT TO ANALYZE:
\"\"\"{state['complaint_text']}\"\"\"

Analyze carefully and return ONLY valid JSON (no markdown, no extra text):

{{
  "severity_level": "low|medium|high|critical",
  "category": "one category from the list above",
  "sentiment_score": [number between -1.0 and 1.0],
  "escalation_required": true|false,
  "key_issues": ["primary issue", "secondary issue if any"],
  "summary_reasoning": "One sentence explaining why you chose this severity level"
}}

JSON:"""

    try:
        result = llm.invoke(prompt)
        data = safe_json_load(result.content)
        
        
        valid_severities = ["low", "medium", "high", "critical"]
        if data.get("severity_level") not in valid_severities:
            logger.warning(f"Invalid severity '{data.get('severity_level')}', defaulting to 'medium'")
            data["severity_level"] = "medium"
        
        
        valid_categories = [
            "maintenance", "cleanliness", "amenities", "service", "billing",
            "noise", "privacy", "safety", "food_beverage", "parking",
            "check_in_out", "general", "positive_feedback"
        ]
        if data.get("category") not in valid_categories:
            logger.warning(f"Invalid category '{data.get('category')}', defaulting to 'general'")
            data["category"] = "general"
        
       
        sentiment = data.get("sentiment_score", 0.0)
        if not isinstance(sentiment, (int, float)) or not (-1.0 <= sentiment <= 1.0):
            logger.warning(f"Invalid sentiment score '{sentiment}', defaulting to 0.0")
            data["sentiment_score"] = 0.0

        
        if data["severity_level"] in ["high", "critical"]:
            data["escalation_required"] = True
        else:
            data["escalation_required"] = False

        
        validated = AnalysisOutput(**data)
        analysis_result = validated.model_dump()
        
        
        state["analysis"] = analysis_result
        state["shared_memory"]["analysis"] = analysis_result
        
        logger.info(
            f"Analysis complete: "
            f"Severity={analysis_result['severity_level']}, "
            f"Category={analysis_result['category']}, "
            f"Sentiment={analysis_result['sentiment_score']:.2f}"
        )
        
    except (ValidationError, Exception) as e:
        logger.error(f"❌ Analysis failed: {e}")
        logger.exception("Full traceback:")
        
        # Fallback analysis
        fallback_analysis = {
            "severity_level": "medium",
            "category": "general",
            "sentiment_score": 0.0,
            "escalation_required": False,
            "key_issues": ["Unable to classify - defaulting to standard handling"],
            "summary_reasoning": "Automatic fallback due to analysis error"
        }
        
        
        state["analysis"] = fallback_analysis
        state["shared_memory"]["analysis"] = fallback_analysis
        
        logger.warning("Using fallback analysis values")

    return state