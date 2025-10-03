"""
Enhanced VK API Service with PostgreSQL integration and regional support.
"""
import logging
import random
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from vk_api import VkApi
    from vk_api.exceptions import VkApiError
except ImportError:
    # Graceful degradation if vk_api is not available
    VkApi = None
    VkApiError = Exception

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None

from ..models.config import AppConfig
from ..web.models import Group, Post
from ..web.database import get_database

logger = logging.getLogger(__name__)


class EnhancedVKService:
    """Enhanced VK API service with regional and database support."""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or AppConfig.from_env()
        self.vk_sessions: Dict[str, VkApi] = {}  # Multiple VK sessions
        self.current_session: Optional[VkApi] = None
        self.db = get_database()
        
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
    
    async def initialize(self) -> bool:
        """Initialize VK service with available tokens."""
        if not VkApi:
            logger.error("VK API library not available")
            return False
            
        if not self.config.vk.tokens:
            logger.error("No VK tokens configured")
            return False
        
        # Initialize VK sessions for different token types
        success_count = 0
        
        # Read tokens
        for i, token in enumerate(self.config.vk.read_tokens or self.config.vk.tokens):
            try:
                session = VkApi(token=token)
                session.get_api().users.get()  # Test connection
                self.vk_sessions[f'read_{i}'] = session
                success_count += 1
                logger.info(f"Initialized read session {i}")
            except Exception as e:
                logger.error(f"Failed to initialize read token {i}: {e}")
        
        # Post tokens
        for i, token in enumerate(self.config.vk.post_tokens or self.config.vk.tokens):
            try:
                session = VkApi(token=token)
                session.get_api().users.get()  # Test connection
                self.vk_sessions[f'post_{i}'] = session
                success_count += 1
                logger.info(f"Initialized post session {i}")
            except Exception as e:
                logger.error(f"Failed to initialize post token {i}: {e}")
        
        if success_count > 0:
            self.current_session = list(self.vk_sessions.values())[0]
            logger.info(f"VK service initialized with {success_count} sessions")
            return True
        else:
            logger.error("No VK sessions could be initialized")
            return False
    
    async def get_posts_by_region(self, region: str, count: int = 20) -> List[Dict[str, Any]]:
        """Get posts from VK groups for a specific region."""
        try:
            # Get groups for the region from database
            groups = await self._get_groups_by_region(region)
            if not groups:
                logger.warning(f"No groups found for region: {region}")
                return []
            
            all_posts = []
            read_session = self._get_read_session()
            
            if not read_session:
                logger.error("No read session available")
                return []
            
            for group in groups:
                try:
                    group_posts = await self._fetch_posts_from_group(read_session, group.group_id, count)
                    # Add region info to posts
                    for post in group_posts:
                        post['region'] = region
                        post['source_group'] = group.name
                    all_posts.extend(group_posts)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error fetching posts from group {group.name}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_posts)} posts from {len(groups)} groups in region {region}")
            return all_posts
            
        except Exception as e:
            logger.error(f"Error getting posts by region {region}: {e}")
            return []
    
    async def publish_to_groups(self, post_data: Dict[str, Any], target_groups: List[str]) -> Dict[str, Any]:
        """Publish a post to multiple VK groups."""
        results = {'success': [], 'failed': [], 'total': len(target_groups)}
        
        post_session = self._get_post_session()
        if not post_session:
            logger.error("No post session available")
            return results
        
        for group_id in target_groups:
            try:
                # Format the post
                formatted_text = self._format_post_text(post_data)
                attachments = self._format_attachments(post_data.get('attachments', []))
                
                # Post to VK
                response = post_session.get_api().wall.post(
                    owner_id=int(group_id),
                    message=formatted_text,
                    attachments=attachments,
                    from_group=1
                )
                
                results['success'].append({
                    'group_id': group_id,
                    'post_id': response.get('post_id'),
                    'url': f"https://vk.com/wall{group_id}_{response.get('post_id')}"
                })
                
                logger.info(f"Successfully posted to group {group_id}")
                
                # Delay between posts to avoid rate limiting
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Failed to post to group {group_id}: {e}")
                results['failed'].append({
                    'group_id': group_id,
                    'error': str(e)
                })
                
                # Shorter delay on error
                await asyncio.sleep(1)
        
        logger.info(f"Published to {len(results['success'])}/{len(target_groups)} groups")
        return results
    
    def _get_read_session(self) -> Optional[VkApi]:
        """Get a random read session."""
        read_sessions = [s for k, s in self.vk_sessions.items() if k.startswith('read_')]
        if not read_sessions:
            # Fallback to any available session
            return list(self.vk_sessions.values())[0] if self.vk_sessions else None
        return random.choice(read_sessions)
    
    def _get_post_session(self) -> Optional[VkApi]:
        """Get a random post session."""
        post_sessions = [s for k, s in self.vk_sessions.items() if k.startswith('post_')]
        if not post_sessions:
            # Fallback to any available session
            return list(self.vk_sessions.values())[0] if self.vk_sessions else None
        return random.choice(post_sessions)
    
    async def _get_groups_by_region(self, region: str) -> List[Group]:
        """Get groups from database by region."""
        try:
            if not Session:
                logger.error("SQLAlchemy not available")
                return []
                
            with self.db.get_session() as session:
                groups = session.query(Group).filter(
                    Group.region == region,
                    Group.platform == 'vk',
                    Group.is_active == True
                ).all()
                return groups
        except Exception as e:
            logger.error(f"Error getting groups for region {region}: {e}")
            return []
    
    async def _fetch_posts_from_group(self, vk_session: VkApi, group_id: str, count: int = 20) -> List[Dict[str, Any]]:
        """Fetch posts from a specific VK group."""
        try:
            response = vk_session.get_api().wall.get(
                owner_id=int(group_id),
                count=min(count, 100),  # VK API limit
                offset=0
            )
            return response.get('items', [])
        except VkApiError as e:
            logger.error(f"VK API error fetching from group {group_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching from group {group_id}: {e}")
            return []
    
    def _format_post_text(self, post_data: Dict[str, Any]) -> str:
        """Format post text with regional tags and signatures."""
        text = post_data.get('text', '')
        region = post_data.get('region', '')
        
        # Add regional hashtags
        if region and region in self.regions:
            region_name = self.regions[region]
            text += f"\n\n#{region} #{region_name.replace(' ', '_')}"
        
        # Limit text length (VK limit is ~4096 characters)
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        return text
    
    def _format_attachments(self, attachments: List[Dict[str, Any]]) -> str:
        """Format VK attachments string."""
        if not attachments:
            return ""
        
        formatted = []
        for att in attachments:
            if att.get('type') in ['photo', 'video', 'audio', 'doc']:
                owner_id = att.get('owner_id', '')
                media_id = att.get('id', '')
                if owner_id and media_id:
                    formatted.append(f"{att['type']}{owner_id}_{media_id}")
        
        return ",".join(formatted[:10])  # VK limit is 10 attachments
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test VK API connection with current tokens."""
        results = {
            'total_tokens': len(self.config.vk.tokens),
            'working_sessions': len(self.vk_sessions),
            'details': []
        }
        
        for session_name, session in self.vk_sessions.items():
            try:
                user_info = session.get_api().users.get()
                results['details'].append({
                    'session': session_name,
                    'status': 'working',
                    'user_id': user_info[0]['id'] if user_info else None
                })
            except Exception as e:
                results['details'].append({
                    'session': session_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    async def get_group_info(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a VK group."""
        session = self._get_read_session()
        if not session:
            return None
        
        try:
            response = session.get_api().groups.getById(
                group_ids=group_id,
                fields='description,members_count,status'
            )
            return response[0] if response else None
        except Exception as e:
            logger.error(f"Error getting group info for {group_id}: {e}")
            return None
    
    def get_regional_hashtags(self, region: str) -> List[str]:
        """Get hashtags for a specific region."""
        base_tags = [f"#{region}"]
        
        if region in self.regions:
            region_name = self.regions[region]
            # Очищаем название региона для тега
            clean_name = region_name.replace(' ', '_').replace("'", '')
            base_tags.append(f"#{clean_name}")
        # Add common regional tags
        base_tags.extend(["#новости", "#регион", "#местныеновости"])
        
        return base_tags


# Legacy compatibility class
class VKService(EnhancedVKService):
    """Legacy VK service for backward compatibility."""
    
    def __init__(self, config: AppConfig = None):
        super().__init__(config)
        logger.warning("Using legacy VKService class. Consider upgrading to EnhancedVKService.")
