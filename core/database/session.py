from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager, contextmanager
from core.config import settings
from sqlalchemy import create_engine


# ✅ Async — for FastAPI routes
async_engine = create_async_engine(settings.DATABASE_ASYNC_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_fastapi():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise

# ✅ Sync — for ProcessPoolExecutor only
sync_engine = create_engine(settings.DATABASE_SYNC_URL, echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine)

@contextmanager
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()