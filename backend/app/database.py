#database.py 

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from .config import DATABASE_URL, REDIS_PORT, REDIS_HOST, REDIS_DB
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# for postgres
# engine = create_engine(DATABASE_URL)

# Create a SQLAlchemy engine with AWS RDS optimizations
engine = create_engine(
    DATABASE_URL,
    pool_size=15,               # Maximum number of connections in the pool
    max_overflow=10,            # Additional connections allowed beyond the pool
    pool_timeout=30,            # Wait time before timeout when no connections are available
    pool_recycle=1800,          # Recycle connections older than 30 minutes
    pool_pre_ping=True          # Test connections before use to avoid stale connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency: Get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()   
        raise e
    finally:
        db.close()  


async def init_db():
    """Asynchronously initialize the database schema."""
    from . import models  
    async with async_engine.begin() as conn:
        print("Initializing database schema...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database schema initialized successfully.")
    

# Asynchronous support for AWS RDS PostgreSQL database
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Generate ASYNC_DATABASE_URL from DATABASE_URL for async use cases
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# async_engine = create_async_engine(
#     ASYNC_DATABASE_URL,
#     pool_size=15,
#     max_overflow=10,
#     pool_timeout=30,
#     pool_recycle=1800,
#     pool_pre_ping=True
# )
async_engine = create_async_engine(ASYNC_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()   
            raise e   
        finally:
            await session.close()
            

import redis
from redis.exceptions import RedisError, ConnectionError

class RedisClient:
    def __init__(self):
        try:
            self.pool = redis.ConnectionPool(
                host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
        except RedisError as e:
            print(f"Redis connection error: {e}")
            self.client = None

    def get_client(self):
        if not self.client:
            raise ConnectionError("Redis client is not initialized.")
        return self.client


# Dependency function  
def get_redis_client() -> redis.Redis:
    redis_client = RedisClient()
    return redis_client.get_client()
