"""API v1 router — aggregates all route modules."""

from fastapi import APIRouter

from app.api.v1 import action_items, auth, meetings, search, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
router.include_router(action_items.router, prefix="/action-items", tags=["Action Items"])
router.include_router(search.router, prefix="/search", tags=["Search"])
