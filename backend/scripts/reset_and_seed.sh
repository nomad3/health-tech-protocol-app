#!/bin/bash
set -e

echo "========================================="
echo "PsyProtocol Database Reset & Seed"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will DROP and RECREATE the database!"
echo "⚠️  All existing data will be LOST!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Starting database reset and seed process..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Change to backend directory
cd "$BACKEND_DIR"

echo "=== Step 1: Load environment variables ==="
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Loaded .env file"
else
    echo "✗ Error: .env file not found"
    exit 1
fi

echo ""
echo "=== Step 2: Extract database name from DATABASE_URL ==="
# Extract database name from DATABASE_URL
# Format: postgresql://user:pass@host:port/dbname
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)$/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\(.*\):.*/\1/p')

echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"

echo ""
echo "=== Step 3: Drop existing database ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";" 2>/dev/null || {
    echo "⚠️  Warning: Could not drop database (it may not exist)"
}
echo "✓ Database dropped (if it existed)"

echo ""
echo "=== Step 4: Create new database ==="
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\";"
echo "✓ Database created"

echo ""
echo "=== Step 5: Run Alembic migrations ==="
alembic upgrade head
echo "✓ Migrations completed"

echo ""
echo "=== Step 6: Run seed script ==="
python seed_database.py

echo ""
echo "========================================="
echo "✓ Database reset and seed COMPLETED!"
echo "========================================="
echo ""
echo "You can now start the application with:"
echo "  uvicorn app.main:app --reload"
echo ""
