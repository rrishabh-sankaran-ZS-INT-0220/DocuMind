import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import AsyncSessionLocal
from backend.app.services.ingestion_manager import IngestionManager

logger = logging.getLogger("documind.ingestion")


async def ingest_document_with_session(db: AsyncSession, document_id: Any) -> None:
    """Run ingestion using a provided AsyncSession.

    This wrapper is primarily useful for tests or internal calls where the
    session lifecycle is already managed externally.
    """
    manager = IngestionManager(db=db)
    await manager.run(document_id=document_id)


async def _run_ingestion_document(document_id: Any) -> None:
    """Internal helper to run ingestion with its own AsyncSession.

    This avoids reusing request-scoped sessions and ensures the background
    ingestion has a complete, independent unit of work.
    """
    async with AsyncSessionLocal() as session:
        await ingest_document_with_session(session, document_id)


def launch_ingestion(document_id: Any) -> None:
    """Launch ingestion in the background, decoupled from request lifecycle.

    This should be called by API handlers after creating the Document row.
    The pipeline manages its own AsyncSession and logs stage-level progress.

    Depending on the deployment model, this implementation can be swapped
    for a proper task queue (e.g., Celery, RQ, or a dedicated worker).
    """
    logger.info(
        "ingestion.launch",
        extra={"document_id": str(document_id)},
    )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop: create a new one and fire-and-forget.
        # This is primarily useful for ad-hoc scripts; in FastAPI we expect a loop.
        logger.warning(
            "ingestion.launch.no_running_loop",
            extra={"document_id": str(document_id)},
        )
        asyncio.run(_run_ingestion_document(document_id))
        return

    # In application context, schedule the task on the existing loop.
    loop.create_task(_run_ingestion_document(document_id))