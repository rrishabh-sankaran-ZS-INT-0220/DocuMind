from functools import lru_cache
from typing import Iterable, List, Optional
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


QDRANT_URL = "http://localhost:6333"
QDRANT_API_KEY: Optional[str] = None  # set if you secure Qdrant


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Return a shared Qdrant client instance."""
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )


def ensure_collection(
    collection_name: str,
    vector_size: int,
    distance: qmodels.Distance = qmodels.Distance.COSINE,
) -> None:
    """Ensure the Qdrant collection exists with the correct configuration."""
    client = get_qdrant_client()

    if client.collection_exists(collection_name):
        return

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance=distance,
        ),
    )


def upsert_document_chunks(
    collection_name: str,
    document_id: UUID,
    texts: Iterable[str],
    vectors: List[list[float]],
    pages: Iterable[int],
    sections: Iterable[Optional[str]],
) -> int:
    """Upsert chunks of a document into Qdrant, returns count of inserted points."""
    client = get_qdrant_client()

    payloads = []
    ids = []
    for idx, (text, page, section) in enumerate(zip(texts, pages, sections)):
        ids.append(f"{document_id}-{idx}")
        payloads.append(
            {
                "document_id": str(document_id),
                "chunk_index": idx,
                "page": page,
                "section": section,
                "text": text,
            }
        )

    client.upsert(
        collection_name=collection_name,
        points=qmodels.Batch(
            ids=ids,
            vectors=vectors,
            payloads=payloads,
        ),
    )

    return len(ids)