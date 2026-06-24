import mimetypes
import os
import uuid
from pathlib import Path
from typing import Iterable

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import Document, User

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

UPLOAD_ROOT = Path("uploads")


def _validate_file_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file extension")


def _infer_mime_type(filename: str) -> str | None:
    mime, _ = mimetypes.guess_type(filename)
    return mime


async def _validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Unsupported MIME type")

    # Read limited bytes to enforce max size
    file_size = 0
    chunk = await file.read(1024 * 1024)
    while chunk:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError("File too large")
        chunk = await file.read(1024 * 1024)

    await file.seek(0)


async def create_document(
    db: AsyncSession,
    user: User,
    file: UploadFile,
) -> Document:
    """Create a Document row and store the uploaded file."""
    _validate_file_extension(file.filename)
    await _validate_file(file)

    document_id = uuid.uuid4()

    user_dir = UPLOAD_ROOT / str(user.id)
    doc_dir = user_dir / str(document_id)
    os.makedirs(doc_dir, exist_ok=True)

    file_path = doc_dir / file.filename

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    await file.seek(0)

    document = Document(
        id=document_id,
        title=file.filename,
        original_filename=file.filename,
        content_type=file.content_type or _infer_mime_type(file.filename),
        status="uploaded",
        owner_id=user.id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


async def list_documents(db: AsyncSession, user: User) -> list[Document]:
    result = await db.execute(select(Document).where(Document.owner_id == user.id))
    return list(result.scalars().all())


async def get_document(db: AsyncSession, user: User, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == user.id)
    )
    return result.scalars().first()


async def delete_document(db: AsyncSession, user: User, document: Document) -> None:
    # Delete file directory if present
    doc_dir = UPLOAD_ROOT / str(user.id) / str(document.id)
    if doc_dir.exists():
        for root, dirs, files in os.walk(doc_dir, topdown=False):
            for name in files:
                os.remove(Path(root) / name)
            for name in dirs:
                os.rmdir(Path(root) / name)
        os.rmdir(doc_dir)

    await db.delete(document)
    await db.commit()