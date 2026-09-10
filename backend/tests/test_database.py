from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_session_reaches_postgres(db_session: AsyncSession) -> None:
    """The suite runs against a real PostgreSQL, never SQLite."""
    result = await db_session.execute(text("SELECT version()"))
    version = result.scalar_one()

    assert version.startswith("PostgreSQL 16")
