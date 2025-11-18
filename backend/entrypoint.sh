#!/bin/bash
set -e

echo "=================================="
echo "Database Initialization Script"
echo "=================================="

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
python << END
import time
import asyncpg
import asyncio

async def wait_for_db():
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            conn = await asyncpg.connect(
                host="${DATABASE_HOST:-waste-postgres}",
                port=int("${DATABASE_PORT:-5432}"),
                user="${DATABASE_USER:-waste_user}",
                password="${DATABASE_PASSWORD:-waste_password}",
                database="${DATABASE_NAME:-waste_db}"
            )
            await conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except Exception as e:
            print(f"⏳ Attempt {i+1}/{max_retries}: Waiting for PostgreSQL...")
            time.sleep(retry_interval)
    
    print("❌ Failed to connect to PostgreSQL")
    return False

if not asyncio.run(wait_for_db()):
    exit(1)
END

# Initialize database tables
echo "Initializing database tables..."
python << END
from app.core.database import init_db
import asyncio

try:
    asyncio.run(init_db())
    print("✅ Database tables initialized!")
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")
    exit(1)
END

# Check if SEED_DATA environment variable is set
if [ "${SEED_DATA:-false}" = "true" ]; then
    echo "=================================="
    echo "Seeding Database with Mock Data"
    echo "=================================="
    
    # Run seeding script
    python -m app.seed_data ${SEED_COUNT:-100}
    
    echo "✅ Database seeding completed!"
else
    echo "Skipping database seeding (SEED_DATA not set to true)"
fi

echo "=================================="
echo "Starting FastAPI Application"
echo "=================================="

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
