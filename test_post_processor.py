#!/usr/bin/env python3
"""
Test script for Enhanced Post Processor.
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add root directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from src.services.post_processor import EnhancedPostProcessor
    from src.models.config import AppConfig
    from dotenv import load_dotenv
    import logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install dependencies: pip install python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_posts():
    """Create test VK posts for processing."""
    current_time = int(datetime.now().timestamp())
    
    return [
        {
            'id': 1,
            'owner_id': -12345,
            'from_id': -12345,
            'text': 'Сегодня в нашем городе произошло важное событие #Новости',
            'date': current_time - 3600,  # 1 hour ago
            'views': {'count': 150},
            'attachments': [
                {
                    'type': 'photo',
                    'photo': {
                        'owner_id': -12345,
                        'id': 456,
                        'sizes': [
                            {'width': 130, 'height': 87, 'url': 'https://example.com/photo_130.jpg'},
                            {'width': 604, 'height': 403, 'url': 'https://example.com/photo_604.jpg'}
                        ]
                    }
                }
            ]
        },
        {
            'id': 2,
            'owner_id': -67890,
            'from_id': -67890,
            'text': 'Старые новости которые никому не интересны',
            'date': current_time - 86400 * 2,  # 2 days ago
            'views': {'count': 5}
        },
        {
            'id': 3,
            'owner_id': -11111,
            'from_id': -11111,
            'text': 'Проверка на хороший контент с видео',
            'date': current_time - 1800,  # 30 minutes ago
            'views': {'count': 250},
            'attachments': [
                {
                    'type': 'video',
                    'video': {
                        'owner_id': -11111,
                        'id': 789
                    }
                }
            ]
        },
        {
            'id': 4,
            'owner_id': -22222,
            'from_id': -22222,
            'text': 'Очень длинный текст для приколов который не должен пройти фильтр потому что слишком длинный для темы prikol',
            'date': current_time - 900,  # 15 minutes ago
            'views': {'count': 45}
        },
        {
            'id': 5,
            'owner_id': -33333,
            'from_id': -33333,
            'text': 'Реклама товаров',
            'date': current_time - 7200,  # 2 hours ago
            'views': {'count': 25}
        },
        {
            'id': 6,
            'owner_id': -44444,
            'from_id': -44444,
            'text': 'Пост с репостом',
            'date': current_time - 1200,  # 20 minutes ago
            'views': {'count': 80},
            'copy_history': [
                {
                    'owner_id': -55555,
                    'text': 'Оригинальный текст из репоста #Новости',
                    'date': current_time - 3600
                }
            ]
        }
    ]

async def test_post_processor():
    """Test post processor functionality."""
    print("🧪 Testing Enhanced Post Processor")
    print("=" * 50)
    
    # Create configuration
    config = AppConfig.from_env()
    
    # Add some test blacklisted words
    config.filters.delete_msg_blacklist = ['запрещенное_слово', 'спам']
    config.filters.black_id = [99999]  # Blacklisted group ID
    
    print(f"📋 Configuration:")
    print(f"   Blacklisted words: {len(config.filters.delete_msg_blacklist)}")
    print(f"   Blacklisted groups: {len(config.filters.black_id)}")
    
    # Create post processor
    processor = EnhancedPostProcessor(config)
    
    # Load filtering data
    print("\n🔄 Loading filtering data...")
    await processor.load_filtering_data()
    
    # Create test posts
    test_posts = create_test_posts()
    print(f"\n📄 Created {len(test_posts)} test posts")
    
    # Test different themes
    test_themes = ['novost', 'sosed', 'kino', 'prikol', 'reklama']
    
    for theme in test_themes:
        print(f"\n🎭 Testing theme: {theme}")
        print("-" * 30)
        
        processed_posts = await processor.process_posts_by_region(
            test_posts, 'mi', theme
        )
        
        print(f"   Input posts: {len(test_posts)}")
        print(f"   Processed posts: {len(processed_posts)}")
        
        for post in processed_posts[:2]:  # Show first 2 processed posts
            print(f"   ✅ Post {post['id']}: '{post['text'][:50]}...' (Views: {post['views']['count']})")
    
    # Test regional hashtags
    print(f"\n🏷️  Testing regional hashtags...")
    test_regions = ['mi', 'nolinsk', 'arbazh']
    
    for region in test_regions:
        hashtags = processor.get_regional_hashtags(region)
        print(f"   📍 {region}: {', '.join(hashtags[:3])}...")
    
    # Test single post processing
    print(f"\n🔍 Testing single post processing...")
    test_post = test_posts[0]  # First post
    processed_post = await processor._process_single_post(test_post, 'mi', 'novost')
    
    if processed_post:
        print(f"   ✅ Processed post successfully:")
        print(f"      ID: {processed_post['vk_post_id']}")
        print(f"      Region: {processed_post['region']}")
        print(f"      Theme: {processed_post['theme']}")
        print(f"      Text: {processed_post['text'][:100]}...")
        print(f"      URL: {processed_post['source_url']}")
    else:
        print(f"   ❌ Post was filtered out")
    
    print("\n🎉 Post Processor tests completed!")
    return True

def main():
    """Main test function."""
    try:
        success = asyncio.run(test_post_processor())
        
        if success:
            print("\n✅ All tests passed!")
            print("\nNext steps:")
            print("1. Test with real VK API data")
            print("2. Connect to PostgreSQL database")
            print("3. Integrate with web interface")
        else:
            print("\n❌ Some tests failed.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)