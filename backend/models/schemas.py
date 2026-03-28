# backend/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ClaimStatus(str, Enum):
    VERIFIED     = "VERIFIED"
    UNCERTAIN    = "UNCERTAIN"
    CONTRADICTED = "CONTRADICTED"


class VerifyRequest(BaseModel):
    query: str


class ClaimResult(BaseModel):
    text:         str
    status:       ClaimStatus
    source_url:   Optional[str] = None
    source_title: Optional[str] = None


class SentenceAnnotation(BaseModel):
    text:       str
    status:     str
    claim_ref:  Optional[str] = None
    source_url: Optional[str] = None


class VerifyResponse(BaseModel):
    trust_score:      int
    answer:           str
    confidence:       int
    verifier_used:    bool
    claims:           List[ClaimResult]
    sentences:        List[SentenceAnnotation]
    from_cache:       bool
    latency_ms:       int
    error:            Optional[str]  = None
    trust_label:      Optional[str]  = None
    trust_color:      Optional[str]  = None
    bias_score:       Optional[int]  = None
    toxicity_score:   Optional[int]  = None
    intent_aligned:   Optional[bool] = None
    alignment_score:  Optional[int]  = None
    bias_flags:       Optional[list] = None
