from fastapi import FastAPI
from fastapi_pagination import add_pagination
from taxis.router import router as taxis_router

app = FastAPI(
    title="Taxi",
    description="Taxi dispatch service simulator",
    debug=True,
)

app.include_router(taxis_router)
add_pagination(app)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
