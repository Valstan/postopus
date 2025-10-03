#!/usr/bin/env python3
"""
Create Postopus tables in existing mikrokredit database.
This script will add Postopus tables to your existing database without affecting other data.
"""
import asyncio
import asyncpg
import os
from datetime import datetime


async def create_postopus_tables():
    """Create Postopus-specific tables in the existing mikrokredit database."""
    
    # Database connection
    DATABASE_URL = "postgresql://mikrokredit_user:6xoKkR0wfL1Zc0YcmqcE4GSjBSXlQ8Rv@dpg-ctlcj5pu0jms73a6qfvg-a.oregon-postgres.render.com/mikrokredit"
    
    print("🔗 Connecting to mikrokredit database...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected successfully!")
        
        # Create tables for Postopus
        print("📋 Creating Postopus tables...")
        
        # Users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS postopus_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role VARCHAR(20) DEFAULT 'editor',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        print("✅ Created postopus_users table")
        
        # Posts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS postopus_posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                region VARCHAR(20) NOT NULL,
                theme VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'draft',
                image_url VARCHAR(500),
                video_url VARCHAR(500),
                vk_group_id VARCHAR(50),
                telegram_chat_id VARCHAR(50),
                tags JSONB DEFAULT '[]',
                priority INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                source_url VARCHAR(500),
                post_metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_at TIMESTAMP,
                published_at TIMESTAMP
            );
        """)
        print("✅ Created postopus_posts table")
        
        # Settings table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS postopus_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'general',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created postopus_settings table")
        
        # VK Tokens table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS postopus_vk_tokens (
                id SERIAL PRIMARY KEY,
                region VARCHAR(20) UNIQUE NOT NULL,
                token VARCHAR(500) NOT NULL,
                group_id VARCHAR(50) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP
            );
        """)
        print("✅ Created postopus_vk_tokens table")
        
        # Groups table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS postopus_groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                region VARCHAR(20) NOT NULL,
                vk_group_id VARCHAR(50),
                telegram_chat_id VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created postopus_groups table")
        
        # Create indexes for better performance
        print("🔍 Creating indexes...")
        
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_posts_region ON postopus_posts(region);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_posts_theme ON postopus_posts(theme);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_posts_status ON postopus_posts(status);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_posts_created_at ON postopus_posts(created_at);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_settings_category ON postopus_settings(category);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_postopus_vk_tokens_region ON postopus_vk_tokens(region);")
        
        print("✅ Created indexes")
        
        # Insert default admin user (password: admin)
        hashed_admin_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewgPajMkxmksOI5u"  # bcrypt hash of "admin"
        
        await conn.execute("""
            INSERT INTO postopus_users (username, email, hashed_password, full_name, role, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (username) DO NOTHING;
        """, "admin", "admin@postopus.ru", hashed_admin_password, "System Administrator", "admin", True)
        
        await conn.execute("""
            INSERT INTO postopus_users (username, email, hashed_password, full_name, role, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (username) DO NOTHING;
        """, "editor", "$2b$12$6RNDz5gB8XzPyBQY8G9jQeJ8dZr5mI5CQ1L9n3xM8lY6Kj3Ej5KjG", "Content Editor", "editor", True)
        
        print("✅ Created default users (admin/admin, editor/editor123)")
        
        # Insert default settings
        default_settings = [
            ("site_name", "Postopus", "general", "System name"),
            ("default_region", "mi", "posting", "Default region for new posts"),
            ("auto_publish_delay", "300", "posting", "Default delay between posts in seconds"),
            ("vk_api_version", "5.131", "vk", "VK API version to use"),
            ("max_posts_per_hour", "10", "posting", "Maximum posts to publish per hour")
        ]
        
        for key, value, category, description in default_settings:
            await conn.execute("""
                INSERT INTO postopus_settings (key, value, category, description)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (key) DO NOTHING;
            """, key, value, category, description)
        
        print("✅ Created default settings")
        
        # Insert default regional groups
        regions = [
            ("Малмыж", "mi"), ("Нолинск", "nolinsk"), ("Арбаж", "arbazh"),
            ("Кирс", "kirs"), ("Слободской", "slob"), ("Верхошиженье", "verhosh"),
            ("Богородское", "bogord"), ("Яранск", "yaransk"), ("Вятские Поляны", "viatpol"),
            ("Зуна", "zuna"), ("Даровской", "darov"), ("Килмезь", "kilmez"),
            ("Лебяжье", "lebazh"), ("Омутнинск", "omut"), ("Санчурск", "san")
        ]
        
        for name, region in regions:
            await conn.execute("""
                INSERT INTO postopus_groups (name, region, is_active)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING;
            """, name, region, True)
        
        print("✅ Created regional groups")
        
        # Check table creation
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'postopus_%'
            ORDER BY table_name;
        """)
        
        print(f"\n📊 Created {len(tables)} Postopus tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        await conn.close()
        print("\n🎉 Postopus tables created successfully in mikrokredit database!")
        print("\n🔐 Default users created:")
        print("  - admin/admin (Administrator)")
        print("  - editor/editor123 (Content Editor)")
        print("\n🌍 15 regional groups configured")
        print("⚙️ Default settings applied")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Setting up Postopus tables in mikrokredit database...")
    print("📍 Database: mikrokredit")
    print("👤 User: mikrokredit_user")
    print("🏠 Host: dpg-ctlcj5pu0jms73a6qfvg-a.oregon-postgres.render.com")
    print()
    
    success = asyncio.run(create_postopus_tables())
    
    if success:
        print("\n✅ Setup completed! Your mikrokredit database now contains Postopus tables.")
        print("🚀 Ready for deployment to Render.com!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")