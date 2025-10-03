#!/usr/bin/env python3
"""
Test script to verify PostgreSQL migration and schema creation.
"""
import os
import sys
from pathlib import Path

# Add root directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    import logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install dependencies: pip install python-dotenv sqlalchemy psycopg2-binary")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgres_connection():
    """Test PostgreSQL connection."""
    print("🔄 Testing PostgreSQL connection...")
    
    # Get DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Build from components
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'postopus')
        user = os.getenv('POSTGRES_USER', 'postopus')
        password = os.getenv('POSTGRES_PASSWORD', 'postopus_password')
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connection successful!")
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_schema_creation():
    """Test schema creation."""
    print("\n🔄 Testing schema creation...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'postopus')
        user = os.getenv('POSTGRES_USER', 'postopus')
        password = os.getenv('POSTGRES_PASSWORD', 'postopus_password')
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    try:
        engine = create_engine(database_url)
        
        # Simple schema test
        test_schema = """
        -- Test table creation
        CREATE TABLE IF NOT EXISTS test_posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            region VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Test index creation
        CREATE INDEX IF NOT EXISTS idx_test_posts_region ON test_posts(region);
        
        -- Test insert
        INSERT INTO test_posts (title, content, region) 
        VALUES ('Test Post', 'This is a test post', 'mi')
        ON CONFLICT DO NOTHING;
        
        -- Test select
        SELECT COUNT(*) FROM test_posts;
        """
        
        with engine.connect() as connection:
            # Execute schema creation
            connection.execute(text(test_schema))
            connection.commit()
            
            # Test query
            result = connection.execute(text("SELECT COUNT(*) FROM test_posts"))
            count = result.scalar()
            
            print(f"✅ Schema creation successful!")
            print(f"   Test records: {count}")
            
            # Cleanup
            connection.execute(text("DROP TABLE IF EXISTS test_posts"))
            connection.commit()
            
            return True
            
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

def check_environment():
    """Check environment variables."""
    print("🔄 Checking environment configuration...")
    
    required_vars = ['MONGO_CLIENT']
    optional_vars = ['DATABASE_URL', 'POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    
    print("\n📋 Required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"   ❌ {var}: Not set")
    
    print("\n📋 Optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            # Hide passwords
            if 'PASSWORD' in var or 'URL' in var:
                masked_value = value[:10] + '***' if len(value) > 10 else '***'
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚪ {var}: Using default")

def main():
    """Main test function."""
    print("🧪 Postopus Migration Test Suite")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Test PostgreSQL connection
    if not test_postgres_connection():
        print("\n❌ Database connection test failed. Check your PostgreSQL configuration.")
        return False
    
    # Test schema creation
    if not test_schema_creation():
        print("\n❌ Schema creation test failed.")
        return False
    
    print("\n🎉 All tests passed! Ready for migration.")
    print("\nNext steps:")
    print("1. Run: python improved_migration.py")
    print("2. Check migration.log for detailed logs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)