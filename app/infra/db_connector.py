import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(dotenv_path="./env/.env")


__DB_DIALECT = "postgresql"
__DB_USER = "gentle"
__DB_PASSWD = "password"
__DB_PORT = "5432"
__DB_NAME = "gentle"
__DB_CONTAINER_NAME = "gentle-db"

DATABASE_URL = f"{__DB_DIALECT}://{__DB_USER}:{__DB_PASSWD}@{__DB_CONTAINER_NAME}:{__DB_PORT}/{__DB_NAME}"
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)

async_engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session():
    async_session = AsyncSessionLocal()
    try:
        yield async_session
        await async_session.commit()
    finally:
        await async_session.close()
