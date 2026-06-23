from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentBase(BaseModel):
    title: str
    status: str


class DocumentCreate(BaseModel):
    title: str


class DocumentResponse(DocumentBase):
    id: UUID
    original_filename: str
    content_type: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
