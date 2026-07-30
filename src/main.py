from fastapi import FastAPI

from src.api.v1.contest_lists import router as university_router

app = FastAPI()

app.include_router(university_router)


@app.get("/")
async def root():
    return {"status": 200}
