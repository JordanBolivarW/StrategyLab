import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.main import create_app
from src.database import Base, get_db_session
from src.models import User, Strategy, StrategyVersion


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSession = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSession() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


def _valid_graph():
    return {
        "nodes": [
            {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
            {"id": "2", "type": "indicator.sma", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
            {"id": "3", "type": "indicator.sma", "position": {"x": 200, "y": 100}, "data": {"period": 50}},
            {"id": "4", "type": "logic.cross_above", "position": {"x": 400, "y": 50}, "data": {}},
            {"id": "5", "type": "action.buy", "position": {"x": 600, "y": 50}, "data": {}},
            {"id": "6", "type": "action.close", "position": {"x": 600, "y": 150}, "data": {}},
        ],
        "edges": [
            {"id": "e1", "source": "1", "target": "2"},
            {"id": "e2", "source": "1", "target": "3"},
            {"id": "e3", "source": "2", "target": "4", "sourceHandle": "value", "targetHandle": "a"},
            {"id": "e4", "source": "3", "target": "4", "sourceHandle": "value", "targetHandle": "b"},
            {"id": "e5", "source": "4", "target": "5", "sourceHandle": "result", "targetHandle": "condition"},
            {"id": "e6", "source": "4", "target": "6", "sourceHandle": "result", "targetHandle": "condition"},
        ],
        "metadata": {},
    }


@pytest_asyncio.fixture
async def seeded_version(db_session):
    user = User(email="bt@example.com", name="BT User")
    db_session.add(user)
    await db_session.flush()

    graph = _valid_graph()
    strategy = Strategy(
        user_id=user.id,
        name="BT Strategy",
        description="backtest fixture",
        market="BTCUSDT",
        timeframe="1h",
        graph=graph,
        current_version=1,
    )
    db_session.add(strategy)
    await db_session.flush()

    version = StrategyVersion(
        strategy_id=strategy.id,
        version=1,
        graph=graph,
        changelog="Initial version",
        created_by="user",
        source="web",
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    await db_session.refresh(strategy)
    return version


def _payload(version, strategy_id=None):
    return {
        "strategy_version_id": str(version.id),
        "config": {
            "strategy_id": strategy_id or str(version.strategy_id),
            "market": "BTCUSDT",
            "timeframe": "1h",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-02-01T00:00:00",
            "initial_capital": 10000.0,
            "commission": 0.001,
            "slippage": 0.0005,
        },
    }


class TestBacktestsAPI:
    async def test_create_backtest(self, client, seeded_version):
        resp = await client.post("/api/v1/backtests", json=_payload(seeded_version))
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] in ("pending", "running", "completed")
        assert body["strategy_version_id"] == str(seeded_version.id)
        assert body["strategy_id"] == str(seeded_version.strategy_id)

    async def test_create_backtest_completes(self, client, seeded_version):
        resp = await client.post("/api/v1/backtests", json=_payload(seeded_version))
        assert resp.status_code == 201
        created = resp.json()
        body = (await client.get(f"/api/v1/backtests/{created['id']}")).json()
        assert body["status"] == "completed"
        assert body["metrics"] is not None
        assert body["metrics"]["initial_capital"] == 10000.0
        assert len(body["equity_curve"]) > 0
        assert isinstance(body["trades"], list)

    async def test_create_backtest_canonicalizes_strategy_id(self, client, seeded_version):
        other = str(uuid.uuid4())
        resp = await client.post("/api/v1/backtests", json=_payload(seeded_version, strategy_id=other))
        assert resp.status_code == 201
        assert resp.json()["config"]["strategy_id"] == str(seeded_version.strategy_id)

    async def test_create_backtest_unknown_version(self, client):
        resp = await client.post(
            "/api/v1/backtests",
            json=_payload(type("V", (), {"id": uuid.uuid4(), "strategy_id": uuid.uuid4()})()),
        )
        assert resp.status_code == 404

    async def test_create_backtest_invalid_body(self, client):
        resp = await client.post("/api/v1/backtests", json={"strategy_version_id": str(uuid.uuid4())})
        assert resp.status_code == 422

    async def test_get_backtest(self, client, seeded_version):
        created = (await client.post("/api/v1/backtests", json=_payload(seeded_version))).json()
        resp = await client.get(f"/api/v1/backtests/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_backtest_not_found(self, client):
        resp = await client.get(f"/api/v1/backtests/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_list_backtests(self, client, seeded_version):
        await client.post("/api/v1/backtests", json=_payload(seeded_version))
        await client.post("/api/v1/backtests", json=_payload(seeded_version))
        resp = await client.get("/api/v1/backtests")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2
        assert len(resp.json()["items"]) == 2

    async def test_list_backtests_status_filter(self, client, seeded_version):
        await client.post("/api/v1/backtests", json=_payload(seeded_version))
        resp = await client.get("/api/v1/backtests", params={"status": "completed"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        resp = await client.get("/api/v1/backtests", params={"status": "bogus"})
        assert resp.status_code == 422

    async def test_delete_backtest(self, client, seeded_version):
        created = (await client.post("/api/v1/backtests", json=_payload(seeded_version))).json()
        resp = await client.delete(f"/api/v1/backtests/{created['id']}")
        assert resp.status_code == 204
        assert (await client.get(f"/api/v1/backtests/{created['id']}")).status_code == 404
