from functools import lru_cache
from typing import Iterable, List

from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-large-en-v1.5"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the sentence-transformers embedding model."""
    model = SentenceTransformer(MODEL_NAME)
    return model


def embed_texts(texts: Iterable[str]) -> List[list[float]]:
    """Embed a list of texts using the shared model."""
    model = get_embedding_model()
    # bge-large encourages normalized embeddings; we keep raw floats here
    vectors = model.encode(
        list(texts),
        batch_size=16,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    # Convert to plain Python lists for Qdrant client
    return [v.tolist() for v in vectors]