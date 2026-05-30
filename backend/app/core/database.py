"""Database connections — PostgreSQL (SQLAlchemy async), Redis, Neo4j."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ─── PostgreSQL ────────────────────────────────────────────────────────────────

# Convert postgres:// → postgresql+asyncpg://
_db_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(_db_url, echo=settings.APP_ENV == "development", pool_size=10)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup (dev only — use Alembic in production)."""
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            # Import all models so Base knows about them
            from app.models import action_item, meeting, user  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)


# ─── Redis ────────────────────────────────────────────────────────────────────

import redis.asyncio as aioredis

redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL, encoding="utf-8", decode_responses=True
)


async def get_redis() -> aioredis.Redis:
    return redis_client


# ─── Neo4j ────────────────────────────────────────────────────────────────────

from neo4j import AsyncGraphDatabase

neo4j_driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
)


async def get_neo4j():
    async with neo4j_driver.session() as session:
        yield session
