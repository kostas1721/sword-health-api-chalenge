from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/recommendations"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    recommendation = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_recommendation(record):
    async with async_session() as session:
        session.add(Recommendation(**record))
        await session.commit()

async def get_recommendation_by_id(rec_id: str):
    async with async_session() as session:
        result = await session.get(Recommendation, rec_id)
        return result.__dict__ if result else None
