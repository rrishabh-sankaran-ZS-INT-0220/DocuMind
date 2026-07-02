import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import Document, User
from backend.app.db.session import get_db
from backend.app.schemas.documents import DocumentResponse
from backend.app.services.document_service import (
    create_document,
    delete_document,
    get_document,
    list_documents,
)
from backend.app.services.ingestion import ingest_document
from backend.app.dependencies import get_current_user
from backend.app.core.rate_limit import build_rate_limiter
from backend.app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])
upload_rate_limiter = build_rate_limiter(
    limit=settings.upload_rate_limit_requests,
    window_seconds=settings.upload_rate_limit_window_seconds,
    limiter_name="upload",
)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _rate_limit: None = Depends(upload_rate_limiter),
) -> Document:
    """Upload a document for the authenticated user.

    Supported types: PDF, DOCX, TXT, MD.
    Triggers async ingestion (parse → chunk → embed → Qdrant).
    """

    try:
        document = await create_document(db=db, user=current_user, file=file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # Trigger ingestion in background
    background_tasks.add_task(ingest_document, db, document.id)

    return document


@router.get("", response_model=list[DocumentResponse])
async def list_user_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    """List documents belonging to the authenticated user."""
    return await list_documents(db=db, user=current_user)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_user_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    """Get a single document by ID for the authenticated user."""
    document = await get_document(db=db, user=current_user, document_id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}/status", response_model=dict)
async def get_document_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get status of a document (uploaded, processing, ready, failed)."""
    document = await get_document(db=db, user=current_user, document_id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {
        "id": str(document.id),
        "status": document.status,
        "error_message": document.error_message,
        "vector_collection": document.vector_collection,
        "vector_count": document.vector_count,
    }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a document and its stored files for the authenticated user."""
    document = await get_document(db=db, user=current_user, document_id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    await delete_document(db=db, user=current_user, document=document)