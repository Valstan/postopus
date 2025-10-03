#!/usr/bin/env python3
"""
Enhanced PostgreSQL Migration Script for Postopus
Migrates data from MongoDB to PostgreSQL with improved schema and error handling.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add root directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    from sqlalchemy import create_engine, text, Index
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import SQLAlchemyError
    import psycopg2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install dependencies: pip install pymongo sqlalchemy psycopg2-binary python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMigrator:
    """Enhanced migrator with improved error handling and schema."""
    
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_CLIENT', 'mongodb://localhost:27017/')
        self.postgres_url = self._get_postgres_url()
        self.mongo_client = None
        self.mongo_db = None
        self.postgres_engine = None
        self.postgres_session = None
        
        # Regional mapping for 15 regions
        self.regions = {
            'mi': 'Malmyž',
            'nolinsk': 'Nolinsk', 
            'arbazh': 'Arbazh',
            'nema': 'Nema',
            'ur': 'Uržum',
            'verhoshizhem': 'Verhošižem\'e',
            'klz': 'Kil\'mez\'',
            'pizhanka': 'Pižanka',
            'afon': 'Afon',
            'kukmor': 'Kukmor',
            'sovetsk': 'Sovetsk',
            'malmigrus': 'Malmyž Groups',
            'vp': 'Vjatskie Poljany',
            'leb': 'Lebjaž\'e',
            'dran': 'Dran',
            'bal': 'Baltasi'
        }
    
    def _get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL from environment."""
        # Try DATABASE_URL first (for Render.com)
        url = os.getenv('DATABASE_URL')
        if url:
            return url
            
        # Build from individual components
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'postopus')
        user = os.getenv('POSTGRES_USER', 'postopus')
        password = os.getenv('POSTGRES_PASSWORD', 'postopus_password')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    def connect_mongo(self) -> bool:
        """Connect to MongoDB."""
        try:
            self.mongo_client = MongoClient(self.mongo_url)
            self.mongo_db = self.mongo_client['postopus']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected MongoDB error: {e}")
            return False
    
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL."""
        try:
            self.postgres_engine = create_engine(self.postgres_url, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.postgres_engine)
            self.postgres_session = SessionLocal()
            
            # Test connection
            with self.postgres_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("✅ Connected to PostgreSQL successfully")
                return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def create_enhanced_schema(self):
        """Create enhanced PostgreSQL schema with proper indexes."""
        logger.info("🔄 Creating enhanced PostgreSQL schema...")
        
        schema_sql = """
        -- Drop existing tables if they exist
        DROP TABLE IF EXISTS posts CASCADE;
        DROP TABLE IF EXISTS groups CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS schedules CASCADE;
        DROP TABLE IF EXISTS migrations CASCADE;
        
        -- Posts table with regional support
        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            image_url VARCHAR(500),
            video_url VARCHAR(500),
            status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'scheduled', 'archived')),
            region VARCHAR(100),
            source_collection VARCHAR(100),
            vk_group_id VARCHAR(100),
            telegram_chat_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            scheduled_at TIMESTAMP,
            published_at TIMESTAMP,
            metadata JSONB DEFAULT '{}',
            tags TEXT[] DEFAULT '{}',
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0
        );
        
        -- Groups table for social media groups
        CREATE TABLE groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL CHECK (platform IN ('vk', 'telegram', 'ok', 'instagram')),
            group_id VARCHAR(100) NOT NULL,
            region VARCHAR(100),
            access_token VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            settings JSONB DEFAULT '{}',
            stats JSONB DEFAULT '{}',
            UNIQUE(platform, group_id)
        );
        
        -- Users table with role-based access
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP,
            permissions JSONB DEFAULT '{}',
            settings JSONB DEFAULT '{}'
        );
        
        -- Schedules table for Celery tasks
        CREATE TABLE schedules (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            cron_expression VARCHAR(100) NOT NULL,
            task_name VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_run TIMESTAMP,
            next_run TIMESTAMP,
            run_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            parameters JSONB DEFAULT '{}',
            results JSONB DEFAULT '{}'
        );
        
        -- Migration tracking table
        CREATE TABLE migrations (
            id SERIAL PRIMARY KEY,
            version VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            executed_at TIMESTAMP DEFAULT NOW(),
            execution_time_ms INTEGER,
            success BOOLEAN DEFAULT TRUE,
            details JSONB DEFAULT '{}'
        );
        
        -- Indexes for performance
        CREATE INDEX idx_posts_status ON posts(status);
        CREATE INDEX idx_posts_region ON posts(region);
        CREATE INDEX idx_posts_created_at ON posts(created_at);
        CREATE INDEX idx_posts_published_at ON posts(published_at);
        CREATE INDEX idx_posts_scheduled_at ON posts(scheduled_at);
        CREATE INDEX idx_posts_content_gin ON posts USING gin(to_tsvector('english', content));
        CREATE INDEX idx_posts_metadata ON posts USING gin(metadata);
        
        CREATE INDEX idx_groups_platform ON groups(platform);
        CREATE INDEX idx_groups_region ON groups(region);
        CREATE INDEX idx_groups_active ON groups(is_active);
        
        CREATE INDEX idx_users_username ON users(username);
        CREATE INDEX idx_users_email ON users(email);
        CREATE INDEX idx_users_active ON users(is_active);
        
        CREATE INDEX idx_schedules_active ON schedules(is_active);
        CREATE INDEX idx_schedules_next_run ON schedules(next_run);
        
        -- Create trigger for updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER update_groups_updated_at BEFORE UPDATE ON groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        try:
            with self.postgres_engine.connect() as connection:
                connection.execute(text(schema_sql))
                connection.commit()
            logger.info("✅ Enhanced schema created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating schema: {e}")
            raise
    
    def migrate_posts(self) -> int:
        """Migrate posts from regional MongoDB collections."""
        logger.info("🔄 Starting posts migration...")
        
        migrated_count = 0
        
        try:
            # Get all collection names
            collections = self.mongo_db.list_collection_names()
            
            # Filter regional collections (exclude system collections)
            regional_collections = [col for col in collections 
                                  if col in self.regions.keys()]
            
            logger.info(f"Found {len(regional_collections)} regional collections")
            
            for collection_name in regional_collections:
                logger.info(f"📄 Processing collection: {collection_name}")
                collection = self.mongo_db[collection_name]
                
                # Get all documents from collection
                documents = list(collection.find({}))
                logger.info(f"Found {len(documents)} documents in {collection_name}")
                
                for doc in documents:
                    try:
                        # Extract content from 'lip' field (array of texts) or other fields
                        content = ""
                        if 'lip' in doc and isinstance(doc['lip'], list):
                            content = ' '.join(str(item) for item in doc['lip'] if item)
                        elif 'text' in doc:
                            content = str(doc['text'])
                        elif 'content' in doc:
                            content = str(doc['content'])
                        else:
                            content = f"Post from {collection_name}"
                        
                        # Skip empty content
                        if not content.strip():
                            continue
                        
                        # Insert post
                        insert_sql = """
                        INSERT INTO posts (
                            title, content, region, source_collection,
                            vk_group_id, telegram_chat_id, status,
                            created_at, metadata
                        ) VALUES (
                            %(title)s, %(content)s, %(region)s, %(source_collection)s,
                            %(vk_group_id)s, %(telegram_chat_id)s, %(status)s,
                            %(created_at)s, %(metadata)s
                        )
                        """
                        
                        values = {
                            'title': doc.get('title', f'Post from {self.regions.get(collection_name, collection_name)}'),
                            'content': content[:10000],  # Limit content length
                            'region': collection_name,
                            'source_collection': collection_name,
                            'vk_group_id': str(doc.get('post_group_vk', doc.get('group_id', ''))),
                            'telegram_chat_id': str(doc.get('post_group_telega', doc.get('telegram_chat_id', ''))),
                            'status': doc.get('status', 'published'),
                            'created_at': doc.get('created_at', datetime.utcnow()),
                            'metadata': json.dumps({
                                'mongo_id': str(doc.get('_id')),
                                'original_data': {k: v for k, v in doc.items() 
                                               if k not in ['_id', 'lip', 'text', 'content'] and len(str(v)) < 1000}
                            })
                        }
                        
                        with self.postgres_engine.connect() as connection:
                            connection.execute(text(insert_sql), values)
                            connection.commit()
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error migrating document from {collection_name}: {e}")
                        continue
                
                logger.info(f"✅ Collection {collection_name} processed")
            
            logger.info(f"✅ Posts migration completed. Migrated: {migrated_count} posts")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Error in posts migration: {e}")
            return migrated_count
    
    def migrate_groups(self) -> int:
        """Migrate groups from MongoDB config."""
        logger.info("🔄 Starting groups migration...")
        
        migrated_count = 0
        
        try:
            # Get config collection
            config_collection = self.mongo_db['config']
            config_doc = config_collection.find_one({'title': 'config'})
            
            if config_doc and 'all_my_groups' in config_doc:
                groups_data = config_doc['all_my_groups']
                logger.info(f"Found {len(groups_data)} groups in config")
                
                for group_name, group_id in groups_data.items():
                    try:
                        # Determine region from group name
                        region = None
                        for region_code, region_name in self.regions.items():
                            if region_code in group_name.lower() or region_name.lower() in group_name.lower():
                                region = region_code
                                break
                        
                        insert_sql = """
                        INSERT INTO groups (
                            name, platform, group_id, region,
                            is_active, created_at, settings
                        ) VALUES (
                            %(name)s, %(platform)s, %(group_id)s, %(region)s,
                            %(is_active)s, %(created_at)s, %(settings)s
                        ) ON CONFLICT (platform, group_id) DO NOTHING
                        """
                        
                        values = {
                            'name': group_name,
                            'platform': 'vk',  # Assuming VK for now
                            'group_id': str(group_id),
                            'region': region,
                            'is_active': True,
                            'created_at': datetime.utcnow(),
                            'settings': json.dumps({
                                'mongo_source': 'config.all_my_groups',
                                'original_id': group_id
                            })
                        }
                        
                        with self.postgres_engine.connect() as connection:
                            connection.execute(text(insert_sql), values)
                            connection.commit()
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error migrating group {group_name}: {e}")
                        continue
            
            logger.info(f"✅ Groups migration completed. Migrated: {migrated_count} groups")
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Error in groups migration: {e}")
            return migrated_count
    
    def create_default_user(self) -> int:
        """Create default admin user."""
        logger.info("🔄 Creating default admin user...")
        
        try:
            # Check if admin user already exists
            check_sql = "SELECT COUNT(*) FROM users WHERE username = 'admin'"
            with self.postgres_engine.connect() as connection:
                result = connection.execute(text(check_sql))
                count = result.scalar()
                
                if count > 0:
                    logger.info("Admin user already exists")
                    return 0
            
            # Create admin user with bcrypt hashed password
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_password = pwd_context.hash("admin")
            except ImportError:
                # Fallback to simple hash if bcrypt not available
                import hashlib
                hashed_password = hashlib.sha256("admin".encode()).hexdigest()
            
            insert_sql = """
            INSERT INTO users (
                username, email, hashed_password, full_name,
                is_active, is_admin, created_at
            ) VALUES (
                %(username)s, %(email)s, %(hashed_password)s, %(full_name)s,
                %(is_active)s, %(is_admin)s, %(created_at)s
            )
            """
            
            values = {
                'username': 'admin',
                'email': 'admin@postopus.local',
                'hashed_password': hashed_password,
                'full_name': 'Administrator',
                'is_active': True,
                'is_admin': True,
                'created_at': datetime.utcnow()
            }
            
            with self.postgres_engine.connect() as connection:
                connection.execute(text(insert_sql), values)
                connection.commit()
            
            logger.info("✅ Default admin user created (admin/admin)")
            return 1
            
        except Exception as e:
            logger.error(f"❌ Error creating default user: {e}")
            return 0
    
    def record_migration(self, name: str, start_time: datetime, success: bool, details: dict):
        """Record migration execution."""
        try:
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            insert_sql = """
            INSERT INTO migrations (
                version, name, executed_at, execution_time_ms, success, details
            ) VALUES (
                %(version)s, %(name)s, %(executed_at)s, %(execution_time_ms)s, %(success)s, %(details)s
            )
            """
            
            values = {
                'version': '1.0.0',
                'name': name,
                'executed_at': datetime.utcnow(),
                'execution_time_ms': execution_time,
                'success': success,
                'details': json.dumps(details)
            }
            
            with self.postgres_engine.connect() as connection:
                connection.execute(text(insert_sql), values)
                connection.commit()
                
        except Exception as e:
            logger.error(f"❌ Error recording migration: {e}")
    
    def run_full_migration(self) -> Dict[str, int]:
        """Run complete migration process."""
        logger.info("🚀 Starting enhanced migration from MongoDB to PostgreSQL...")
        start_time = datetime.utcnow()
        
        try:
            # Connect to databases
            if not self.connect_mongo():
                raise Exception("Failed to connect to MongoDB")
            
            if not self.connect_postgres():
                raise Exception("Failed to connect to PostgreSQL")
            
            # Create enhanced schema
            self.create_enhanced_schema()
            
            # Run migrations
            results = {
                'posts': self.migrate_posts(),
                'groups': self.migrate_groups(),
                'users': self.create_default_user()
            }
            
            # Record successful migration
            self.record_migration("Full Migration", start_time, True, results)
            
            logger.info("🎉 Migration completed successfully!")
            return results
            
        except Exception as e:
            # Record failed migration
            self.record_migration("Full Migration", start_time, False, {'error': str(e)})
            logger.error(f"❌ Migration failed: {e}")
            raise
        
        finally:
            # Clean up connections
            if self.mongo_client:
                self.mongo_client.close()
            if self.postgres_session:
                self.postgres_session.close()

def main():
    """Main function."""
    print("🔄 Enhanced PostgreSQL Migration for Postopus")
    print("=" * 60)
    
    try:
        # Create migrator
        migrator = EnhancedMigrator()
        
        # Run migration
        results = migrator.run_full_migration()
        
        # Display results
        print("\n📊 Migration Results:")
        print("-" * 30)
        for table, count in results.items():
            print(f"  {table}: {count} records")
        
        total = sum(results.values())
        print(f"\n✅ Total migrated: {total} records")
        print(f"📝 Check migration.log for detailed logs")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()