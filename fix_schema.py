import asyncio
from sqlalchemy import text
from app.core.database import engine

async def update_schema():
    async with engine.begin() as conn:
        print("Adding missing columns to epay_invoices...")
        try:
            await conn.execute(text('ALTER TABLE epay_invoices ADD COLUMN IF NOT EXISTS "BookNo" VARCHAR;'))
            await conn.execute(text('ALTER TABLE epay_invoices ADD COLUMN IF NOT EXISTS "billCollector" VARCHAR;'))
            await conn.execute(text('ALTER TABLE epay_invoices ADD COLUMN IF NOT EXISTS "Nazim" VARCHAR;'))
            print("Successfully added missing columns.")
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    asyncio.run(update_schema())
