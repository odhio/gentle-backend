from contextlib import asynccontextmanager
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
engine = create_engine(DATABASE_URL, echo_pool="debug", pool_pre_ping=True)

async_engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


async def get_async_session():
    async_session = AsyncSessionLocal()
    try:
        yield async_session
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    finally:
        await async_session.close()


@asynccontextmanager
async def create_async_session_with_context():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
