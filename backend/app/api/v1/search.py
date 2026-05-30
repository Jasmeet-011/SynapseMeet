"""Semantic search endpoints — powered by Pinecone vector DB."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.services.search import semantic_search

router = APIRouter()


class SearchResult(BaseModel):
    meeting_id: str
    meeting_title: str
    excerpt: str
    score: float
    created_at: str


@router.get("/", response_model=list[SearchResult])
async def search_meetings(
    q: str = Query(..., min_length=2, description="Natural language search query"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Semantic search across all past meeting transcripts and summaries."""
    results = await semantic_search(
        query=q,
        user_id=str(current_user.id),
        workspace_id=str(current_user.workspace_id) if current_user.workspace_id else None,
        limit=limit,
    )
    return results
