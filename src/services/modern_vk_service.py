"""
Modern VK API Service using httpx for Postopus
Enhanced with PostgreSQL integration and regional support.
"""
import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import json

from ..web.database import get_database
from ..web.models import Group, Post, VKToken

logger = logging.getLogger(__name__)


class ModernVKService:
    """Modern VK API service using httpx with regional and database support."""
    
    def __init__(self):
        self.base_url = "https://api.vk.com/method"
        self.api_version = "5.131"
        self.db = get_database()
        self.tokens: Dict[str, VKToken] = {}
        self.rate_limits: Dict[str, float] = {}  # token -> last_request_time
        
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
        """Initialize VK service with tokens from database."""
        try:
            # Load tokens from database
            await self._load_tokens_from_db()
            
            if not self.tokens:
                logger.warning("No VK tokens found in database")
                return False
            
            # Test connections
            working_tokens = 0
            for region, token in self.tokens.items():
                if await self._test_token(token.token):
                    working_tokens += 1
                    logger.info(f"Token for region {region} is working")
                else:
                    logger.warning(f"Token for region {region} is not working")
            
            logger.info(f"VK service initialized with {working_tokens}/{len(self.tokens)} working tokens")
            return working_tokens > 0
            
        except Exception as e:
            logger.error(f"Error initializing VK service: {e}")
            return False
    
    async def _load_tokens_from_db(self):
        """Load VK tokens from database."""
        try:
            session = self.db
            tokens = session.query(VKToken).filter(VKToken.is_active == True).all()
            for token in tokens:
                self.tokens[token.region] = token
            logger.info(f"Loaded {len(tokens)} VK tokens from database")
        except Exception as e:
            logger.error(f"Error loading tokens from database: {e}")
    
    async def _test_token(self, token: str) -> bool:
        """Test if VK token is working."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users.get",
                    params={
                        "access_token": token,
                        "v": self.api_version
                    },
                    timeout=10.0
                )
                data = response.json()
                return "error" not in data
        except Exception as e:
            logger.error(f"Error testing token: {e}")
            return False
    
    async def get_posts_by_region(self, region: str, count: int = 20) -> List[Dict[str, Any]]:
        """Get posts from VK groups for a specific region."""
        try:
            # Get groups for the region from database
            groups = await self._get_groups_by_region(region)
            if not groups:
                logger.warning(f"No groups found for region: {region}")
                return []
            
            # Get token for this region
            token = self.tokens.get(region)
            if not token:
                logger.warning(f"No token found for region: {region}")
                return []
            
            all_posts = []
            
            for group in groups:
                try:
                    group_posts = await self._fetch_posts_from_group(token.token, group.group_id, count)
                    # Add region info to posts
                    for post in group_posts:
                        post['region'] = region
                        post['source_group'] = group.name
                        post['source_group_id'] = group.group_id
                    all_posts.extend(group_posts)
                    
                    # Rate limiting
                    await self._rate_limit(token.token)
                    
                except Exception as e:
                    logger.error(f"Error fetching posts from group {group.name}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_posts)} posts from {len(groups)} groups in region {region}")
            return all_posts
            
        except Exception as e:
            logger.error(f"Error getting posts by region {region}: {e}")
            return []
    
    async def publish_to_groups(self, post_data: Dict[str, Any], target_groups: List[str], region: str = None) -> Dict[str, Any]:
        """Publish a post to multiple VK groups."""
        results = {'success': [], 'failed': [], 'total': len(target_groups)}
        
        # Get token for this region
        token = self.tokens.get(region) if region else list(self.tokens.values())[0]
        if not token:
            logger.error("No token available for publishing")
            return results
        
        for group_id in target_groups:
            try:
                # Format the post
                formatted_text = self._format_post_text(post_data, region)
                attachments = self._format_attachments(post_data.get('attachments', []))
                
                # Post to VK
                response = await self._post_to_vk(token.token, group_id, formatted_text, attachments)
                
                if response and "error" not in response:
                    results['success'].append({
                        'group_id': group_id,
                        'post_id': response.get('post_id'),
                        'url': f"https://vk.com/wall{group_id}_{response.get('post_id')}"
                    })
                    logger.info(f"Successfully posted to group {group_id}")
                else:
                    results['failed'].append({
                        'group_id': group_id,
                        'error': response.get('error', 'Unknown error') if response else 'No response'
                    })
                
                # Rate limiting
                await self._rate_limit(token.token)
                
            except Exception as e:
                logger.error(f"Failed to post to group {group_id}: {e}")
                results['failed'].append({
                    'group_id': group_id,
                    'error': str(e)
                })
        
        logger.info(f"Published to {len(results['success'])}/{len(target_groups)} groups")
        return results
    
    async def _get_groups_by_region(self, region: str) -> List[Group]:
        """Get groups from database by region."""
        try:
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
    
    async def _fetch_posts_from_group(self, token: str, group_id: str, count: int = 20) -> List[Dict[str, Any]]:
        """Fetch posts from a specific VK group."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/wall.get",
                    params={
                        "access_token": token,
                        "owner_id": group_id,
                        "count": min(count, 100),  # VK API limit
                        "offset": 0,
                        "v": self.api_version
                    },
                    timeout=10.0
                )
                data = response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    return []
                
                return data.get('response', {}).get('items', [])
                
        except Exception as e:
            logger.error(f"Error fetching from group {group_id}: {e}")
            return []
    
    async def _post_to_vk(self, token: str, group_id: str, text: str, attachments: str = "") -> Optional[Dict[str, Any]]:
        """Post to VK group."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/wall.post",
                    params={
                        "access_token": token,
                        "owner_id": group_id,
                        "message": text,
                        "attachments": attachments,
                        "from_group": 1,
                        "v": self.api_version
                    },
                    timeout=10.0
                )
                data = response.json()
                return data
                
        except Exception as e:
            logger.error(f"Error posting to group {group_id}: {e}")
            return None
    
    def _format_post_text(self, post_data: Dict[str, Any], region: str = None) -> str:
        """Format post text with regional tags and signatures."""
        text = post_data.get('text', '')
        
        # Add regional hashtags
        if region and region in self.regions:
            region_name = self.regions[region]
            text += f"\n\n#{region} #{region_name.replace(' ', '_')}"
        
        # Add theme hashtags
        theme = post_data.get('theme', '')
        if theme:
            text += f" #{theme}"
        
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
    
    async def _rate_limit(self, token: str):
        """Implement rate limiting for VK API."""
        now = time.time()
        last_request = self.rate_limits.get(token, 0)
        
        # VK API allows 3 requests per second
        if now - last_request < 0.34:  # ~3 requests per second
            await asyncio.sleep(0.34 - (now - last_request))
        
        self.rate_limits[token] = time.time()
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test VK API connection with current tokens."""
        results = {
            'total_tokens': len(self.tokens),
            'working_tokens': 0,
            'details': []
        }
        
        for region, token in self.tokens.items():
            try:
                is_working = await self._test_token(token.token)
                if is_working:
                    results['working_tokens'] += 1
                
                results['details'].append({
                    'region': region,
                    'group_id': token.group_id,
                    'status': 'working' if is_working else 'error',
                    'last_used': token.last_used.isoformat() if token.last_used else None
                })
            except Exception as e:
                results['details'].append({
                    'region': region,
                    'group_id': token.group_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    async def get_group_info(self, group_id: str, token: str = None) -> Optional[Dict[str, Any]]:
        """Get information about a VK group."""
        if not token:
            token = list(self.tokens.values())[0].token
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/groups.getById",
                    params={
                        "access_token": token,
                        "group_ids": group_id,
                        "fields": "description,members_count,status",
                        "v": self.api_version
                    },
                    timeout=10.0
                )
                data = response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    return None
                
                groups = data.get('response', [])
                return groups[0] if groups else None
                
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
    
    async def save_post_to_db(self, post_data: Dict[str, Any]) -> Optional[int]:
        """Save post to database."""
        try:
            with self.db.get_session() as session:
                post = Post(
                    title=post_data.get('title', ''),
                    content=post_data.get('text', ''),
                    region=post_data.get('region', ''),
                    theme=post_data.get('theme', ''),
                    status='pending',
                    vk_post_id=post_data.get('id'),
                    vk_group_id=post_data.get('source_group_id'),
                    created_at=datetime.utcnow()
                )
                session.add(post)
                session.commit()
                session.refresh(post)
                return post.id
        except Exception as e:
            logger.error(f"Error saving post to database: {e}")
            return None
    
    async def update_post_status(self, post_id: int, status: str, vk_post_id: str = None):
        """Update post status in database."""
        try:
            with self.db.get_session() as session:
                post = session.query(Post).filter(Post.id == post_id).first()
                if post:
                    post.status = status
                    if vk_post_id:
                        post.vk_post_id = vk_post_id
                    if status == 'published':
                        post.published_at = datetime.utcnow()
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating post status: {e}")


# Backward compatibility
class VKService(ModernVKService):
    """Legacy VK service for backward compatibility."""
    
    def __init__(self):
        super().__init__()
        logger.warning("Using legacy VKService class. Consider upgrading to ModernVKService.")
