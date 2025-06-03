from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_async_engine(
    settings.apg_dsn,
    pool_size=10,
    max_overflow=20,
    echo=False,
)
Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
