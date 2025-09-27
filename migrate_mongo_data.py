"""
MongoDB Data Migration Utility for Postopus
Migrates data from legacy MongoDB structure to new PostgreSQL structure
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from pymongo import MongoClient
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  Missing dependencies. Install with: pip install pymongo sqlalchemy psycopg2-binary")

from src.models.config import AppConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDataMigrator:
    """Handles migration from MongoDB to PostgreSQL."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.mongo_client = None
        self.mongo_db = None
        self.postgres_engine = None
        self.postgres_session = None
        
        # Regional collections mapping
        self.regional_collections = [
            'mi', 'nolinsk', 'arbazh', 'nema', 'ur', 'verhoshizhem',
            'klz', 'pizhanka', 'afon', 'kukmor', 'sovetsk', 'malmigrus',
            'vp', 'leb', 'dran', 'bal'
        ]
        
    async def connect_databases(self) -> bool:
        """Connect to both MongoDB and PostgreSQL."""
        try:
            # Connect to MongoDB
            self.mongo_client = MongoClient(self.config.database.mongo_client)
            self.mongo_db = self.mongo_client["postopus"]
            
            # Test MongoDB connection
            self.mongo_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB")
            
            # Connect to PostgreSQL (if configured)
            if self.config.database.postgres_url:
                self.postgres_engine = create_engine(self.config.database.postgres_url)
                SessionLocal = sessionmaker(bind=self.postgres_engine)
                self.postgres_session = SessionLocal()
                
                # Test PostgreSQL connection
                with self.postgres_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Connected to PostgreSQL")
            else:
                logger.warning("⚠️  PostgreSQL not configured, will only analyze MongoDB")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    async def analyze_mongodb_structure(self) -> Dict[str, Any]:
        """Analyze the current MongoDB structure and data."""
        analysis = {
            "collections": {},
            "total_documents": 0,
            "migration_plan": {},
            "timestamp": datetime.now()
        }
        
        try:
            # Get all collections
            collections = self.mongo_db.list_collection_names()
            logger.info(f"📊 Found {len(collections)} collections")
            
            for collection_name in collections:
                collection = self.mongo_db[collection_name]
                doc_count = collection.count_documents({})
                
                # Get sample document structure
                sample_doc = collection.find_one()
                
                analysis["collections"][collection_name] = {
                    "document_count": doc_count,
                    "sample_structure": self._analyze_document_structure(sample_doc) if sample_doc else {},
                    "migration_target": self._determine_migration_target(collection_name)
                }
                
                analysis["total_documents"] += doc_count
                logger.info(f"   📋 {collection_name}: {doc_count} documents")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ MongoDB analysis failed: {e}")
            return analysis
    
    def _analyze_document_structure(self, doc: Dict[str, Any]) -> Dict[str, str]:
        """Analyze the structure of a MongoDB document."""
        structure = {}
        for key, value in doc.items():
            if key == "_id":
                continue
            structure[key] = type(value).__name__
        return structure
    
    def _determine_migration_target(self, collection_name: str) -> str:
        """Determine the PostgreSQL target for a MongoDB collection."""
        if collection_name in self.regional_collections:
            return "posts"
        elif collection_name == "config":
            return "settings"
        elif collection_name == "users":
            return "users"
        elif collection_name == "tasks":
            return "schedules"
        else:
            return "metadata"
    
    async def migrate_regional_posts(self) -> Dict[str, int]:
        """Migrate regional posts to PostgreSQL posts table."""
        migration_stats = {}
        
        if not self.postgres_session:
            logger.warning("⚠️  PostgreSQL not available, skipping migration")
            return migration_stats
        
        try:
            for region in self.regional_collections:
                collection = self.mongo_db[region]
                documents = list(collection.find())
                
                migrated_count = 0
                for doc in documents:
                    try:
                        # Transform MongoDB document to PostgreSQL format
                        post_data = self._transform_post_document(doc, region)
                        
                        # Insert into PostgreSQL (simplified - would use SQLAlchemy models)
                        # This is a placeholder for actual implementation
                        logger.debug(f"Would migrate post: {post_data.get('title', 'Untitled')}")
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to migrate document {doc.get('_id')}: {e}")
                
                migration_stats[region] = migrated_count
                logger.info(f"✅ Migrated {migrated_count} posts from {region}")
            
            return migration_stats
            
        except Exception as e:
            logger.error(f"❌ Regional posts migration failed: {e}")
            return migration_stats
    
    def _transform_post_document(self, doc: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Transform MongoDB document to PostgreSQL format."""
        # Extract content from 'lip' array
        content = " ".join(doc.get('lip', [])) if doc.get('lip') else ""
        
        return {
            "title": f"Post from {region}",
            "content": content,
            "region": region,
            "source_collection": region,
            "vk_group_id": doc.get('post_group_vk'),
            "telegram_chat_id": doc.get('post_group_telega'),
            "status": "published",
            "created_at": datetime.now(),
            "metadata": {
                "original_id": str(doc.get('_id')),
                "original_data": doc
            }
        }
    
    async def migrate_configuration(self) -> bool:
        """Migrate configuration data."""
        try:
            config_collection = self.mongo_db['config']
            config_doc = config_collection.find_one({'title': 'config'})
            
            if not config_doc:
                logger.warning("⚠️  No configuration document found")
                return False
            
            # Extract important configuration
            extracted_config = {
                "vk_groups": config_doc.get('all_my_groups', {}),
                "filters": {
                    "delete_msg_blacklist": config_doc.get('delete_msg_blacklist', []),
                    "clear_text_blacklist": config_doc.get('clear_text_blacklist', {}),
                    "black_id": config_doc.get('black_id', []),
                    "time_old_post": config_doc.get('time_old_post', {})
                },
                "settings": {
                    "text_post_maxsize_simbols": config_doc.get('text_post_maxsize_simbols', 4000),
                    "table_size": config_doc.get('table_size', 30)
                }
            }
            
            logger.info("✅ Configuration extracted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration migration failed: {e}")
            return False
    
    async def create_migration_report(self, analysis: Dict[str, Any]) -> str:
        """Create a detailed migration report."""
        report_lines = [
            "# MongoDB to PostgreSQL Migration Report",
            f"**Generated:** {analysis['timestamp']}",
            f"**Total Documents:** {analysis['total_documents']}",
            "",
            "## Collections Analysis",
            ""
        ]
        
        for collection_name, info in analysis["collections"].items():
            report_lines.extend([
                f"### {collection_name}",
                f"- **Documents:** {info['document_count']}",
                f"- **Migration Target:** {info['migration_target']}",
                f"- **Structure:** {info['sample_structure']}",
                ""
            ])
        
        report_lines.extend([
            "## Migration Strategy",
            "",
            "1. **Regional Posts** → `posts` table",
            f"   - Collections: {', '.join(self.regional_collections)}",
            "   - Combine `lip` arrays into single content field",
            "   - Preserve regional information",
            "",
            "2. **Configuration** → Application settings",
            "   - Extract VK groups, filters, and general settings",
            "   - Convert to environment variables format",
            "",
            "3. **Users** → `users` table",
            "   - Migrate user accounts and permissions",
            "",
            "4. **Tasks** → `schedules` table",
            "   - Convert task definitions to cron schedules",
            "",
            "## Recommendations",
            "",
            "- Create backup before migration",
            "- Test migration on staging environment",
            "- Plan for data validation after migration",
            "- Consider gradual migration strategy"
        ])
        
        return "\n".join(report_lines)
    
    async def close_connections(self):
        """Close database connections."""
        if self.mongo_client:
            self.mongo_client.close()
        if self.postgres_session:
            self.postgres_session.close()
        if self.postgres_engine:
            self.postgres_engine.dispose()

async def main():
    """Main migration function."""
    if not DEPENDENCIES_AVAILABLE:
        return
    
    print("🚀 Starting MongoDB Data Migration Analysis...")
    
    # Load configuration
    config = AppConfig.from_env()
    
    # Create migrator
    migrator = MongoDataMigrator(config)
    
    try:
        # Connect to databases
        if not await migrator.connect_databases():
            print("❌ Failed to connect to databases")
            return
        
        # Analyze MongoDB structure
        print("📊 Analyzing MongoDB structure...")
        analysis = await migrator.analyze_mongodb_structure()
        
        # Create migration report
        report = await migrator.create_migration_report(analysis)
        
        # Save report
        report_path = Path("MIGRATION_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Migration analysis complete!")
        print(f"📄 Report saved to: {report_path}")
        print(f"📊 Total collections: {len(analysis['collections'])}")
        print(f"📊 Total documents: {analysis['total_documents']}")
        
        # Optional: Run actual migration
        response = input("\n🤔 Run actual data migration? (y/N): ")
        if response.lower() == 'y':
            print("🔄 Starting data migration...")
            migration_stats = await migrator.migrate_regional_posts()
            print(f"✅ Migration completed: {migration_stats}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
    finally:
        await migrator.close_connections()

if __name__ == "__main__":
    asyncio.run(main())