from enum import Enum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, HttpUrl

# 1. Enums: Enforce strict categories to avoid hallucination
class EvidenceSource(str, Enum):
    PUBMED = "PubMed"
    WHO = "WHO"
    CDC = "CDC"
    NICE = "NICE"
    FDA = "FDA"
    COCHRANE = "Cochrane"

class EvidenceLevel(str, Enum):
    GUIDELINE = "guideline"
    META_ANALYSIS = "meta-analysis"
    RCT = "RCT"
    COHORT = "cohort"
    REVIEW = "review"
    CASE = "case"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# 2. Input Model
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=10, description="The user's medical question")
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age in years")
    sex: Optional[str] = None
    context: Optional[str] = Field(None, description="Known conditions, allergies, or medications")

# 3. Evidence Model
class EvidenceChunk(BaseModel):
    source: EvidenceSource
    title: str
    authors: str
    year: int = Field(..., ge=1900, le=2026) 
    pmid_or_doi: Optional[str] = None
    url: HttpUrl # Validates real URL structure
    evidence_level: str
    excerpt: str = Field(..., max_length=150, description="Summarized evidence (≤120-150 chars)")
    relevance_score: float = Field(..., ge=0.0, le=1.0)

# 4. Main Diagnostic Model
class DiagnosticResponse(BaseModel):
    # reasoning: str = Field(..., description="Step-by-step clinical logic (Chain-of-Thought)")
    answer: str = Field(..., description="The final direct answer to the user")
    key_points: List[str] = [] # Field(..., min_length=1)
    citations: List[EvidenceChunk] = []
    confidence: ConfidenceLevel
    intent: str = Field(..., description="Detected user intent (e.g., info seeking, triage)")
    
    # Safety & Compliance
    is_emergency: bool = Field(False, description="True if symptoms suggest immediate 911/ER visit")
    disclaimer: str = "This is an AI analysis, not a medical diagnosis. Consult a doctor immediately."
    
    # Error Handling
    fallback: bool = False
    fallback_reason: Optional[str] = None
