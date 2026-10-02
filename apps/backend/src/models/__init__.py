from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, String, Text, Integer, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    strategies: Mapped[list["Strategy"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    market: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(20), nullable=False)
    graph: Mapped[dict] = mapped_column(JSON, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="strategies")
    versions: Mapped[list["StrategyVersion"]] = relationship(back_populates="strategy", cascade="all, delete-orphan", order_by="StrategyVersion.version")
    backtests: Mapped[list["Backtest"]] = relationship(back_populates="strategy", cascade="all, delete-orphan")
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="strategy", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_strategies_user_market", "user_id", "market"),)


class StrategyVersion(Base):
    __tablename__ = "strategy_versions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    strategy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    graph: Mapped[dict] = mapped_column(JSON, nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    strategy: Mapped["Strategy"] = relationship(back_populates="versions")
    backtests: Mapped[list["Backtest"]] = relationship("Backtest", back_populates="strategy_version", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("strategy_id", "version", name="uq_strategy_version"),)


class Backtest(Base):
    __tablename__ = "backtests"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    strategy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_version_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("strategy_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    equity_curve: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    trades: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    strategy: Mapped["Strategy"] = relationship(back_populates="backtests")
    strategy_version: Mapped["StrategyVersion"] = relationship(back_populates="backtests")
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="backtest")

    __table_args__ = (Index("ix_backtests_strategy_status", "strategy_id", "status"),)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    market: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    experiments: Mapped[list["Experiment"]] = relationship(back_populates="dataset")

    __table_args__ = (UniqueConstraint("market", "timeframe", "source", "start_date", "end_date", name="uq_dataset"),)


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    strategy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False, index=True)
    base_version: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_version: Mapped[int] = mapped_column(Integer, nullable=False)
    hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dataset_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    backtest_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("backtests.id", ondelete="SET NULL"), nullable=True)
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    strategy: Mapped["Strategy"] = relationship(back_populates="experiments")
    dataset: Mapped["Dataset | None"] = relationship(back_populates="experiments")
    backtest: Mapped["Backtest | None"] = relationship(back_populates="experiments")


# Export all models
__all__ = [
    "User",
    "Strategy",
    "StrategyVersion",
    "Backtest",
    "Dataset",
    "Experiment",
    "Base",
]