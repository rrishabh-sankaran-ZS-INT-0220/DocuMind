import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.db.models import Collection, Document, User
from backend.app.dependencies import get_current_user
from backend.app.schemas.collections import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
    CollectionWithDocuments,
)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Collection:
    """Create a new collection for the current user."""
    collection = Collection(
        name=payload.name,
        owner_id=current_user.id,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Collection]:
    """List collections owned by the current user."""
    stmt = select(Collection).where(Collection.owner_id == current_user.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{collection_id}", response_model=CollectionWithDocuments)
async def get_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionWithDocuments:
    """Get a single collection and its document IDs."""
    stmt = select(Collection).where(
        Collection.id == collection_id,
        Collection.owner_id == current_user.id,
    )
    result = await db.execute(stmt)
    collection = result.scalar_one_or_none()
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    document_ids = [doc.id for doc in collection.documents]
    return CollectionWithDocuments(
        id=collection.id,
        name=collection.name,
        owner_id=collection.owner_id,
        document_ids=document_ids,
    )


@router.patch("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: uuid.UUID,
    payload: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Collection:
    """Update a collection's name."""
    stmt = select(Collection).where(
        Collection.id == collection_id,
        Collection.owner_id == current_user.id,
    )
    result = await db.execute(stmt)
    collection = result.scalar_one_or_none()
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    if payload.name is not None:
        collection.name = payload.name

    await db.commit()
    await db.refresh(collection)
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a collection and unassign its documents."""
    stmt = select(Collection).where(
        Collection.id == collection_id,
        Collection.owner_id == current_user.id,
    )
    result = await db.execute(stmt)
    collection = result.scalar_one_or_none()
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    # Unassign documents from this collection
    for doc in collection.documents:
        doc.collection_id = None

    await db.delete(collection)
    await db.commit()


@router.post("/{collection_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_document_to_collection(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Assign a document to a collection (both must belong to the user)."""
    # Check collection
    stmt_coll = select(Collection).where(
        Collection.id == collection_id,
        Collection.owner_id == current_user.id,
    )
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )

    # Check document
    stmt_doc = select(Document).where(
        Document.id == document_id,
        Document.owner_id == current_user.id,
    )
    result_doc = await db.execute(stmt_doc)
    document = result_doc.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    document.collection_id = collection.id
    await db.commit()


@router.delete("/{collection_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_from_collection(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a document from a collection (set collection_id to null)."""
    stmt_doc = select(Document).where(
        Document.id == document_id,
        Document.owner_id == current_user.id,
        Document.collection_id == collection_id,
    )
    result_doc = await db.execute(stmt_doc)
    document = result_doc.scalar_one_or_none()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this collection",
        )

    document.collection_id = None
    await db.commit()