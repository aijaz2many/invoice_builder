
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_business_schema():
    print("Connecting to database...")
    async with engine.begin() as conn:
        print("Checking for templateStatus column in epay_business...")
        try:
            # Check if column exists
            check_sql = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='epay_business' AND column_name='templateStatus';
            """)
            result = await conn.execute(check_sql)
            column_exists = result.scalar()
            
            if not column_exists:
                print("Adding missing 'templateStatus' column...")
                await conn.execute(text("ALTER TABLE epay_business ADD COLUMN \"templateStatus\" VARCHAR(20) DEFAULT 'MISSING';"))
                print("Column added successfully.")
            else:
                print("Column 'templateStatus' already exists.")
                
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_business_schema())
