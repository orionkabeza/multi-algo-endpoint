import os
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///analysis.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    algo: Mapped[str] = mapped_column(String(64), nullable=False)
    complexity: Mapped[str] = mapped_column(String(32), nullable=False)
    n_min: Mapped[int] = mapped_column(Integer, nullable=False)
    n_max: Mapped[int] = mapped_column(Integer, nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    truncated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    snapshot_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    points: Mapped[List["AnalysisPoint"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="AnalysisPoint.n",
    )


class AnalysisPoint(Base):
    __tablename__ = "analysis_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), nullable=False, index=True)
    n: Mapped[int] = mapped_column(Integer, nullable=False)
    seconds: Mapped[float] = mapped_column(Float, nullable=False)

    analysis: Mapped["Analysis"] = relationship(back_populates="points")


def init_db():
    Base.metadata.create_all(bind=engine)


def save_analysis(result: dict) -> int:
    with SessionLocal() as session:
        analysis = Analysis(
            algo=result["algo"],
            complexity=result["complexity"],
            n_min=result["n_min"],
            n_max=result["n_max"],
            step=result["step"],
            truncated=result["truncated"],
            snapshot_path=result["snapshot_path"],
        )
        analysis.points = [
            AnalysisPoint(n=p["n"], seconds=p["seconds"]) for p in result["points"]
        ]
        session.add(analysis)
        session.commit()
        return analysis.id
