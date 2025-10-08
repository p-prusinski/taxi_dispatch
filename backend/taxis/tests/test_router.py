import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from taxis.models import Taxi


@pytest.mark.asyncio
async def test_get_taxis(db_session: AsyncSession, client: AsyncClient) -> None:
    await Taxi(
        x=1,
        y=12,
    ).create(db_session)
    await Taxi(x=0, y=100).create(db_session)

    response = await client.get("/taxis")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "items": [
            {"x": 1, "y": 12, "status": "AVAILABLE", "pk": 1},
            {"x": 0, "y": 100, "status": "AVAILABLE", "pk": 2},
        ],
        "total": 2,
        "page": 1,
        "size": 50,
        "pages": 1,
    }


@pytest.mark.asyncio
async def test_register_taxi(db_session: AsyncSession, client: AsyncClient) -> None:
    body = {"x": 90, "y": 90}
    response = await client.post("/taxis", json=body)
    assert response.status_code == 200, response.text
    assert response.json() == {"x": 90, "y": 90, "status": "AVAILABLE", "pk": 1}


@pytest.mark.asyncio
async def test_register_taxi_wrong_coords(
    db_session: AsyncSession, client: AsyncClient
) -> None:
    body = {"x": -1, "y": 110}
    response = await client.post("/taxis", json=body)
    assert response.status_code == 422, response.text
    assert response.json() == {
        "detail": [
            {
                "type": "greater_than_equal",
                "loc": ["body", "x"],
                "msg": "Input should be greater than or equal to 0",
                "input": -1,
                "ctx": {"ge": 0},
            },
            {
                "type": "less_than_equal",
                "loc": ["body", "y"],
                "msg": "Input should be less than or equal to 100",
                "input": 110,
                "ctx": {"le": 100},
            },
        ]
    }


@pytest.mark.asyncio
async def test_update_taxi_returns_404(client: AsyncClient) -> None:
    body = {"x": 100, "y": 100}
    response = await client.patch("/taxis/1", json=body)
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "Taxi(pk=1) not found"}


@pytest.mark.asyncio
async def test_update_taxi_updates_status_and_location(
    db_session: AsyncSession, client: AsyncClient
) -> None:
    await Taxi(x=0, y=0).create(db_session)
    body = {"x": 100, "y": 100}
    response = await client.patch("/taxis/1", json=body)
    assert response.status_code == 200, response.text
    assert response.json() == {"x": 100, "y": 100, "status": "AVAILABLE", "pk": 1}
