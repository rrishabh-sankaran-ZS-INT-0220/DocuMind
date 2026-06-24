from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CollectionBase(BaseModel):
    name: str = Field(..., max_length=255, description="Collection/workspace name")


class CollectionCreate(CollectionBase):
    """Payload to create a new collection."""
    pass


class CollectionUpdate(BaseModel):
    """Payload to update an existing collection."""
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="New collection name",
    )


class CollectionResponse(CollectionBase):
    """Collection response with IDs."""
    id: UUID
    owner_id: UUID

    class Config:
        orm_mode = True


class CollectionWithDocuments(CollectionResponse):
    """Collection plus list of document IDs assigned to it."""
    document_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of documents assigned to this collection",
    )