import pytest
from sqlalchemy import text
from app.database import engine, get_db


def test_database_connection():
    """Test that database connection works."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session():
    """Test database session dependency."""
    db = next(get_db())
    assert db is not None
    db.close()
