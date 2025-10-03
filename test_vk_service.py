#!/usr/bin/env python3
"""
Test script for Enhanced VK Service.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add root directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from src.services.vk_service import EnhancedVKService
    from src.models.config import AppConfig
    from dotenv import load_dotenv
    import logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Install dependencies: pip install vk-api python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vk_service():
    """Test VK service functionality."""
    print("🧪 Testing Enhanced VK Service")
    print("=" * 50)
    
    # Create configuration
    config = AppConfig.from_env()
    
    # Check if VK tokens are configured
    if not config.vk.tokens:
        print("⚠️  No VK tokens configured. Please set VK_TOKENS in .env file")
        print("   Example: VK_TOKENS=token1,token2,token3")
        return False
    
    print(f"📋 Configuration loaded:")
    print(f"   VK tokens: {len(config.vk.tokens)}")
    print(f"   Read tokens: {len(config.vk.read_tokens)}")
    print(f"   Post tokens: {len(config.vk.post_tokens)}")
    
    # Create VK service
    vk_service = EnhancedVKService(config)
    
    # Test initialization
    print("\n🔄 Testing VK service initialization...")
    success = await vk_service.initialize()
    
    if not success:
        print("❌ VK service initialization failed")
        return False
    
    print("✅ VK service initialized successfully")
    
    # Test connection
    print("\n🔄 Testing VK API connections...")
    connection_results = await vk_service.test_connection()
    
    print(f"📊 Connection Results:")
    print(f"   Total tokens: {connection_results['total_tokens']}")
    print(f"   Working sessions: {connection_results['working_sessions']}")
    
    working_sessions = 0
    for detail in connection_results['details']:
        if detail['status'] == 'working':
            print(f"   ✅ {detail['session']}: Working (User ID: {detail.get('user_id')})")
            working_sessions += 1
        else:
            print(f"   ❌ {detail['session']}: {detail.get('error', 'Unknown error')}")
    
    if working_sessions == 0:
        print("❌ No working VK sessions found")
        return False
    
    # Test regional hashtags
    print("\n🔄 Testing regional hashtags...")
    test_regions = ['mi', 'nolinsk', 'arbazh']
    
    for region in test_regions:
        hashtags = vk_service.get_regional_hashtags(region)
        print(f"   📍 {region}: {', '.join(hashtags[:3])}...")
    
    # Test group info (if we have a test group)
    test_group_id = os.getenv('TEST_VK_GROUP_ID')
    if test_group_id:
        print(f"\n🔄 Testing group info for {test_group_id}...")
        group_info = await vk_service.get_group_info(test_group_id)
        
        if group_info:
            print(f"   ✅ Group: {group_info.get('name', 'Unknown')}")
            print(f"   📊 Members: {group_info.get('members_count', 'Unknown')}")
        else:
            print("   ⚠️  Could not get group info (may be private or invalid ID)")
    
    print("\n🎉 VK Service tests completed successfully!")
    return True

def main():
    """Main test function."""
    try:
        success = asyncio.run(test_vk_service())
        
        if success:
            print("\n✅ All tests passed!")
            print("\nNext steps:")
            print("1. Configure VK group IDs in database")
            print("2. Set up regional post processing")
            print("3. Test posting to groups")
        else:
            print("\n❌ Some tests failed. Check configuration.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)