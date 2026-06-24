from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["high", "medium", "low", "not_found"]


class SourceCitation(BaseModel):
    document_id: str
    document_title: Optional[str] = None
    page: int
    section: Optional[str] = None
    snippet: str
    score: float


class QARequest(BaseModel):
    question: str = Field(..., description="User question to ask over documents")
    collection_name: Optional[str] = Field(
        default=None,
        description="Optional Qdrant collection override; default is documents_bge_large",
    )
    top_k: int = Field(default=10, ge=1, le=50)


class QAResponse(BaseModel):
    answer: str
    confidence: ConfidenceLevel
    score: float
    sources: List[SourceCitation]


class MCQOption(BaseModel):
    id: str = Field(..., description="Option identifier, e.g. 'A', 'B', 'C'")
    text: str


class MCQRequest(BaseModel):
    question: str
    options: List[MCQOption]
    collection_name: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)


class MCQOptionScore(BaseModel):
    id: str
    score: float
    justification: str


class MCQResponse(BaseModel):
    selected_option_id: Optional[str]
    confidence: ConfidenceLevel
    options: List[MCQOptionScore]
    sources: List[SourceCitation]


# Session-related schemas

class QAMessageBase(BaseModel):
    role: str  # 'user' | 'assistant'
    content: str
    message_type: str = "open_ended"


class QAMessageResponse(QAMessageBase):
    id: UUID
    session_id: UUID
    confidence: Optional[str] = None

    class Config:
        orm_mode = True


class QASessionCreate(BaseModel):
    title: Optional[str] = None
    document_ids: List[UUID] = Field(
        default_factory=list,
        description="Optional initial set of documents for the session",
    )


class QASessionResponse(BaseModel):
    id: UUID
    title: Optional[str]
    is_active: bool
    user_id: UUID

    class Config:
        orm_mode = True


class QASessionWithMessages(QASessionResponse):
    messages: List[QAMessageResponse] = Field(default_factory=list)