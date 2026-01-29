"""
Pydantic models for type safety and validation
"""
from typing import List, Dict, Any, TypedDict, Optional
from pydantic import BaseModel, Field


class AnalysisOutput(BaseModel):
    """Output schema for Analysis Agent"""
    severity_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    category: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    escalation_required: bool
    key_issues: List[str]
    summary_reasoning: str = Field(
        description="Concise justification without step-by-step reasoning"
    )


class ActionItem(BaseModel):
    """Single action item in the action plan"""
    action: str = Field(..., description="Specific action to take")
    responsible: str = Field(..., description="Department or role")
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    timeline: str = Field(..., description="When to complete")


class ActionPlanOutput(BaseModel):
    """Output schema for Action Planning Agent"""
    internal_actions: List[ActionItem] = Field(..., min_items=1)
    assigned_department: str
    estimated_resolution_time: str
    compensation_recommended: Optional[str] = None
    guest_response_tone: str = Field(default="professional and empathetic")
    response_focus: List[str] = Field(default_factory=list)


class ResponseOutput(BaseModel):
    """Output schema for Response Agent"""
    guest_response: str = Field(..., min_length=50)


class ComplaintState(TypedDict):
    """
    Shared state passed between agents
    """
    # Input fields
    guest_name: str
    room_number: str
    contact_info: str
    complaint_text: str
    
    # ✅ ADD THIS:
    shared_memory: Dict[str, Any]
    
    # Agent outputs (kept for compatibility)
    analysis: Dict[str, Any]
    actions: Dict[str, Any]
    response: Dict[str, Any]
    
    # Status flags
    stored_successfully: bool
    notification_sent: bool