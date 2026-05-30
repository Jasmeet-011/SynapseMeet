"""Semantic search service using Pinecone + sentence-transformers."""

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

from app.core.config import settings

# Lazy-loaded to avoid slow startup
_model: SentenceTransformer | None = None
_pinecone_index = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        _pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    return _pinecone_index


async def embed_text(text: str) -> list[float]:
    """Generate a vector embedding for the given text."""
    import asyncio

    model = get_embedding_model()
    loop = asyncio.get_event_loop()
    embedding = await loop.run_in_executor(None, model.encode, text)
    return embedding.tolist()


async def index_meeting(meeting_id: str, title: str, content: str, metadata: dict):
    """Store meeting embedding in Pinecone for later search."""
    vector = await embed_text(f"{title}\n{content}")
    index = get_pinecone_index()

    index.upsert(
        vectors=[
            {
                "id": meeting_id,
                "values": vector,
                "metadata": {
                    "title": title,
                    "user_id": metadata.get("user_id", ""),
                    "workspace_id": metadata.get("workspace_id", ""),
                    "created_at": metadata.get("created_at", ""),
                    "excerpt": content[:300],
                },
            }
        ]
    )


async def semantic_search(
    query: str,
    user_id: str,
    workspace_id: str | None,
    limit: int = 10,
) -> list[dict]:
    """Run a semantic search query against Pinecone."""
    query_vector = await embed_text(query)
    index = get_pinecone_index()

    filter_condition = {"user_id": user_id}
    if workspace_id:
        filter_condition = {"workspace_id": workspace_id}

    results = index.query(
        vector=query_vector,
        top_k=limit,
        include_metadata=True,
        filter=filter_condition,
    )

    return [
        {
            "meeting_id": match["id"],
            "meeting_title": match["metadata"].get("title", ""),
            "excerpt": match["metadata"].get("excerpt", ""),
            "score": round(match["score"], 4),
            "created_at": match["metadata"].get("created_at", ""),
        }
        for match in results.get("matches", [])
    ]
