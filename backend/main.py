from fastapi import FastAPI

app = FastAPI(
    title="Taxi",
    description="Taxi dispatch service simulator",
    debug=True,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
