import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from database import async_engine, DATABASE_URL
from sql_models import Base
from sqlalchemy import text

async def test_connection():
    """Test MySQL database connection"""
    print("🔍 Testing MySQL Database Connection...")
    print(f"📡 Connection URL: {DATABASE_URL.replace('Bbc@org26.', '***')}")
    
    try:
        # Test basic connection
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ Basic connection test: {test_value}")
            
            # Test database info
            result = await conn.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.scalar()
            print(f"✅ Current database: {current_db}")
            
            # Test version
            result = await conn.execute(text("SELECT VERSION() as version"))
            version = result.scalar()
            print(f"✅ MySQL version: {version}")
            
            # Test table creation (dry run)
            print("🔧 Testing table creation...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully")
            
            # List created tables
            result = await conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"✅ Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        
        print("\n🎉 MySQL connection test completed successfully!")
        print("✅ Database is ready for use")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Verify your Hostinger MySQL credentials")
        print("2. Check if your IP is whitelisted in Hostinger")
        print("3. Ensure MySQL service is running")
        print("4. Check firewall settings")
        return False
    
    finally:
        await async_engine.dispose()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
