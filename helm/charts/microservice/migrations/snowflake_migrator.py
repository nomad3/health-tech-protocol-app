import os
import sys
import snowflake.connector
import hashlib
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Configuration from Environment Variables
ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
USER = os.getenv('SNOWFLAKE_USER')
PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
ROLE = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
PRIVATE_KEY_PATH = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH')
PRIVATE_KEY_PASSPHRASE = os.getenv('SNOWFLAKE_PRIVATE_KEY_PASSPHRASE')

MIGRATIONS_DIR = Path(__file__).parent
HISTORY_TABLE = f"{DATABASE}.{SCHEMA}.MIGRATION_HISTORY"

def get_connection():
    try:
        conn_params = {
            'account': ACCOUNT,
            'user': USER,
            'warehouse': WAREHOUSE,
            'database': DATABASE,
            'schema': SCHEMA,
            'role': ROLE,
            'autocommit': False
        }

        # Check for Private Key Content (Env Var)
        private_key_content = os.getenv('SNOWFLAKE_PRIVATE_KEY')

        if private_key_content:
            print("🔑 Using Key Pair Authentication (Env Var)")
            # Fix newlines if they were escaped
            if "-----BEGIN PRIVATE KEY-----" not in private_key_content:
                private_key_content = private_key_content.replace("\\n", "\n")

            p_key = serialization.load_pem_private_key(
                private_key_content.encode(),
                password=PRIVATE_KEY_PASSPHRASE.encode() if PRIVATE_KEY_PASSPHRASE else None,
                backend=default_backend()
            )
            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            conn_params['private_key'] = pkb

        elif PRIVATE_KEY_PATH and os.path.exists(PRIVATE_KEY_PATH):
            print(f"🔑 Using Key Pair Authentication (Path: {PRIVATE_KEY_PATH})")
            with open(PRIVATE_KEY_PATH, 'rb') as key_file:
                p_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=PRIVATE_KEY_PASSPHRASE.encode() if PRIVATE_KEY_PASSPHRASE else None,
                    backend=default_backend()
                )
                pkb = p_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                conn_params['private_key'] = pkb
        elif PASSWORD:
            print("🔑 Using Password Authentication")
            conn_params['password'] = PASSWORD
        else:
            print("❌ No authentication method provided (Password, Private Key Path, or Private Key Content)")
            sys.exit(1)

        conn = snowflake.connector.connect(**conn_params)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Snowflake: {e}")
        sys.exit(1)

def init_migration_history(cursor):
    """Create migration history table if it doesn't exist"""
    print(f"🔍 Checking for migration history table: {HISTORY_TABLE}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {HISTORY_TABLE} (
            id INTEGER IDENTITY(1,1),
            filename VARCHAR(255) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            status VARCHAR(20) DEFAULT 'SUCCESS',
            error_message TEXT,
            PRIMARY KEY (id)
        )
    """)
    cursor.execute("COMMIT")

def init_database(cursor):
    """Create database and schemas if they don't exist"""
    print(f"🏗️ Initializing database: {DATABASE}")

    # Create database and warehouse
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cursor.execute(f"CREATE WAREHOUSE IF NOT EXISTS {WAREHOUSE} WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = FALSE")
    cursor.execute(f"USE WAREHOUSE {WAREHOUSE}")
    cursor.execute(f"USE DATABASE {DATABASE}")

    # Create all required schemas
    schemas = ['BRONZE', 'SILVER', 'GOLD', 'BRONZE_SILVER', 'BRONZE_GOLD', 'PUBLIC']
    for schema in schemas:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"  ✅ Schema {schema} ready")

    cursor.execute("COMMIT")
    print(f"✅ Database {DATABASE} initialized")

def get_applied_migrations(cursor):
    """Get list of already applied migrations (latest version)"""
    try:
        cursor.execute(f"""
            SELECT filename, checksum
            FROM {HISTORY_TABLE}
            WHERE status = 'SUCCESS'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY filename ORDER BY applied_at DESC) = 1
        """)
        return {row[0]: row[1] for row in cursor.fetchall()}
    except Exception as e:
        print(f"⚠️ Could not fetch applied migrations: {e}")
        return {}

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of file content"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def run_migrations():
    if not all([ACCOUNT, USER, WAREHOUSE, DATABASE]) or not (PASSWORD or PRIVATE_KEY_PATH):
        print("❌ Missing required Snowflake environment variables.")
        sys.exit(1)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        init_database(cursor)  # Create database and schemas first
        init_migration_history(cursor)
        applied_migrations = get_applied_migrations(cursor)

        # Get all SQL files and sort them
        # We can support a naming convention like V1__description.sql, V2__...
        # For now, we'll just sort alphabetically
        sql_files = sorted(list(MIGRATIONS_DIR.glob('*.sql')))

        if not sql_files:
            print(f"⚠️ No SQL files found in {MIGRATIONS_DIR}")
            return

        print(f"📂 Found {len(sql_files)} migration files.")

        for sql_file in sql_files:
            filename = sql_file.name
            checksum = calculate_checksum(sql_file)

            if filename in applied_migrations:
                if applied_migrations[filename] != checksum:
                    print(f"🔄 Checksum changed for {filename}. Re-applying (assuming declarative object)...")
                else:
                    print(f"⏭️ Skipping {filename} (already applied)")
                    continue

            print(f"🚀 Applying {filename}...")

            try:
                # Read file content
                with open(sql_file, 'r') as f:
                    sql_content = f.read()

                # Filter out empty statements and comment-only lines
                # Split by semicolon, filter, rejoin
                statements = []
                for stmt in sql_content.split(';'):
                    # Remove comments and whitespace
                    clean = '\n'.join(
                        line for line in stmt.strip().split('\n')
                        if line.strip() and not line.strip().startswith('--')
                    )
                    if clean.strip():
                        statements.append(stmt.strip())

                if statements:
                    cleaned_sql = ';\n'.join(statements) + ';'
                    conn.execute_string(cleaned_sql)
                else:
                    print(f"  ⚠️ No executable statements in {filename}")

                # Record success (Upsert/Insert)
                # We use a new row for history tracking
                cursor.execute(f"""
                    INSERT INTO {HISTORY_TABLE} (filename, checksum, status, applied_at)
                    VALUES ('{filename}', '{checksum}', 'SUCCESS', CURRENT_TIMESTAMP())
                """)
                conn.commit()
                print(f"✅ Successfully applied {filename}")

            except Exception as e:
                conn.rollback()
                error_msg = str(e).replace("'", "''") # Escape quotes
                print(f"❌ Failed to apply {filename}: {e}")

                # Record failure
                try:
                    cursor.execute(f"""
                        INSERT INTO {HISTORY_TABLE} (filename, checksum, status, error_message)
                        VALUES ('{filename}', '{checksum}', 'FAILED', '{error_msg}')
                    """)
                    conn.commit()
                except:
                    pass

                sys.exit(1) # Stop on first failure

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migrations()
