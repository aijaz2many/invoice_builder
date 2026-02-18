import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_columns():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'epay_invoices'"))
        columns = [row[0] for row in result.fetchall()]
        print(f"Columns in epay_invoices: {columns}")

if __name__ == "__main__":
    asyncio.run(check_columns())
