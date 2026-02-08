from fastapi import FastAPI
from .core.database import engine, Base
from .routers import auth, users
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on start
    async with engine.begin() as conn:
        # In production this should be managed by Alembic
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Modular FastAPI"}
