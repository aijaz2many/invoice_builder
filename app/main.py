from fastapi import FastAPI
from .core.database import engine, Base
from .routers import auth, users, roles, user_roles, business_types, businesses, customers, invoices, subscriptions
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
app.include_router(roles.router)
app.include_router(user_roles.router)
app.include_router(business_types.router)
app.include_router(businesses.router)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(subscriptions.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Modular FastAPI"}
