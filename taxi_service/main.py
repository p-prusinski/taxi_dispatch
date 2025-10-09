import random
import socket
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from settings import settings
from pydantic import BaseModel
from time import sleep

assigned_taxi_id: int | None = None
grid_size = settings.GRID_SIZE
dispatch_url = settings.DISPATCH_URL

position = (0, 0)

MAX_RETRIES = 15
RETRY_DELAY = 2 

class TripRequest(BaseModel):
    x_start: int
    y_start: int
    x_destination: int
    y_destination: int
    taxi_id: int
    user_id: int
    trip_id: int
    waiting_time_minutes: int
    travel_time_minutes: int


async def register_taxi(callback_url: str) -> int:
    async with httpx.AsyncClient() as client:
        for _ in range(1, MAX_RETRIES):
            try:
                x = random.randint(0, grid_size)
                y = random.randint(0, grid_size)
                body = {
                    "x": x,
                    "y": y,
                    "callback_url": callback_url
                }
                response = await client.post(f"{dispatch_url}/taxis", json=body, timeout=3.0)
                return response.json()["pk"]
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                await asyncio.sleep(RETRY_DELAY)


async def update_position(taxi_pk: int, new_x: int, new_y: int):
    async with httpx.AsyncClient() as client:
        body = {"x": new_x, "y": new_y}
        await client.patch(f"{dispatch_url}/taxis/{taxi_pk}", json=body)


async def send_event_client_pickup(taxi_pk: int, trip_id: int, user_id: int):
    async with httpx.AsyncClient() as client:
        url_params = f"?event_type=client_pickup&taxi_id={taxi_pk}&trip_id={trip_id}&user_id={user_id}"
        await client.post(f"{dispatch_url}/events{url_params}")

async def remove_taxi(taxi_pk: int):
    async with httpx.AsyncClient() as client:
        await client.delete(f"{dispatch_url}/taxis/{taxi_pk}")

@asynccontextmanager
async def startup(app: FastAPI):
    global assigned_taxi_id

    callback_url = f"http://{socket.gethostname()}:8080/receive_trip"

    try:
        assigned_taxi_id = await register_taxi(callback_url)
        print(f"Taxi {socket.gethostname()} registered with pk={assigned_taxi_id}")
    except RuntimeError:
        print(f"Taxi {socket.gethostname()} could not reach Dispatch")

    yield
    await remove_taxi(assigned_taxi_id)
    print("App is shutting down")


app = FastAPI(title="Taxi Microservice", lifespan=startup)

async def handle_logic(trip: TripRequest):

    print(f"Taxi {socket.gethostname()} is driving to the client")
    sleep(trip.waiting_time_minutes)
    
    print(f"Taxi {socket.gethostname()} picked up client {trip.user_id}")
    
    await send_event_client_pickup(trip.taxi_id, trip.trip_id, trip.user_id)
    sleep(trip.travel_time_minutes)
    await update_position(assigned_taxi_id, trip.x_destination, trip.y_destination)

@app.post("/receive_trip")
async def receive_trip(trip: TripRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(handle_logic, trip)



