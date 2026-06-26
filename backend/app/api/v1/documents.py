import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
from backend.app.services.ingestion import launch_ingestion
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    """Upload a document for the authenticated user.

    Supported types: PDF, DOCX, TXT, MD.
    Triggers async ingestion (parse → chunk → embed → Qdrant)
    using a decoupled background pipeline.
    """

    try:
        document = await create_document(db=db, user=current_user, file=file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # Launch ingestion in a background coroutine with its own AsyncSession.
    launch_ingestion(document.id)

    return document