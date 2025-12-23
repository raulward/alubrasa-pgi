
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.frameworks.config import settings

# Create Async Engine
# echo=True can be enabled for debugging SQL queries
engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)

# Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db():
    """
    Dependency for FastAPI to get DB session
    """
    async with AsyncSessionLocal() as session:
        yield session
