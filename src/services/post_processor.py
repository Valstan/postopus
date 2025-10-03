"""
Enhanced Post Processing Service with regional and legacy integration.
"""
import logging
import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = None

from ..models.config import AppConfig
from ..web.models import Post as DBPost, Group
from ..web.database import get_database

logger = logging.getLogger(__name__)


class EnhancedPostProcessor:
    """Enhanced post processor with legacy filtering integration."""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or AppConfig.from_env()
        self.db = get_database()
        
        # Initialize filtering data
        self.blacklisted_words = []
        self.blacklisted_groups = []
        self.processed_posts_cache = set()  # Cache for duplicate checking
        self.image_hashes = set()  # Cache for image duplicate checking
        
        # Regional configuration
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
        
        # Theme-specific settings
        self.theme_settings = {
            'novost': {
                'max_age_hours': 24,
                'require_views': True,
                'max_text_length': 4000,
                'allow_reposts': False
            },
            'sosed': {
                'max_age_hours': 12,
                'require_hashtag': '#Новости',
                'max_text_length': 2000
            },
            'kino': {
                'require_video': True,
                'max_age_hours': 48
            },
            'music': {
                'require_audio': True,
                'max_age_hours': 48
            },
            'prikol': {
                'max_text_length': 100,
                'max_age_hours': 6
            },
            'reklama': {
                'max_age_hours': 72,
                'allow_no_attachments': True
            }
        }
    
    async def load_filtering_data(self):
        """Load blacklists and filtering data from database."""
        try:
            if not Session:
                logger.warning("SQLAlchemy not available, using default filters")
                return
                
            # Load blacklisted words from config
            self.blacklisted_words = self.config.filters.delete_msg_blacklist or []
            
            # Load blacklisted groups
            self.blacklisted_groups = self.config.filters.black_id or []
            
            # Load processed posts from database for duplicate checking
            with self.db.get_session() as session:
                recent_posts = session.query(DBPost).filter(
                    DBPost.created_at > datetime.utcnow() - timedelta(days=7)
                ).all()
                
                for post in recent_posts:
                    if post.post_metadata and 'vk_post_id' in post.post_metadata:
                        self.processed_posts_cache.add(post.post_metadata['vk_post_id'])
            
            logger.info(f"Loaded {len(self.blacklisted_words)} blacklisted words, "
                       f"{len(self.blacklisted_groups)} blacklisted groups, "
                       f"{len(self.processed_posts_cache)} processed posts")
                       
        except Exception as e:
            logger.error(f"Error loading filtering data: {e}")
    
    async def process_posts_by_region(self, posts_data: List[Dict[str, Any]], 
                                    region: str, theme: str = 'novost') -> List[Dict[str, Any]]:
        """Process posts for a specific region with filtering."""
        await self.load_filtering_data()
        
        processed_posts = []
        
        for post_data in posts_data:
            try:
                # Convert VK post data to internal format
                processed_post = await self._process_single_post(post_data, region, theme)
                
                if processed_post:
                    processed_posts.append(processed_post)
                    
            except Exception as e:
                logger.error(f"Error processing post {post_data.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by views count (descending)
        processed_posts.sort(
            key=lambda x: x.get('views', {}).get('count', 0), 
            reverse=True
        )
        
        logger.info(f"Processed {len(processed_posts)}/{len(posts_data)} posts for region {region}")
        return processed_posts
    
    async def _process_single_post(self, post_data: Dict[str, Any], 
                                  region: str, theme: str) -> Optional[Dict[str, Any]]:
        """Process a single post with all filtering rules."""
        # Basic validation
        if not post_data.get('id') or not post_data.get('date'):
            return None
        
        # Create post ID for duplicate checking
        post_id = f"{post_data['owner_id']}_{post_data['id']}"
        
        # Check if already processed
        if post_id in self.processed_posts_cache:
            logger.debug(f"Post {post_id} already processed")
            return None
        
        # Check post age
        if not self._is_post_fresh(post_data, theme):
            logger.debug(f"Post {post_id} is too old")
            return None
        
        # Extract repost content if needed
        post_data = self._extract_repost_content(post_data)
        
        # Check blacklisted sources
        if abs(post_data['owner_id']) in self.blacklisted_groups:
            logger.debug(f"Post {post_id} from blacklisted group")
            return None
        
        # Check blacklisted content
        text = post_data.get('text', '')
        if self._contains_blacklisted_content(text):
            logger.debug(f"Post {post_id} contains blacklisted content")
            return None
        
        # Theme-specific filtering
        if not self._passes_theme_filter(post_data, theme):
            logger.debug(f"Post {post_id} failed theme filter for {theme}")
            return None
        
        # Check for duplicate images/videos
        if self._has_duplicate_media(post_data):
            logger.debug(f"Post {post_id} has duplicate media")
            return None
        
        # Clean and format text
        processed_text = self._clean_text(text, theme)
        
        # Create processed post
        processed_post = {
            'id': post_data['id'],
            'owner_id': post_data['owner_id'],
            'from_id': post_data.get('from_id', post_data['owner_id']),
            'text': processed_text,
            'original_text': text,
            'date': datetime.fromtimestamp(post_data['date']),
            'views': post_data.get('views', {'count': 0}),
            'region': region,
            'theme': theme,
            'attachments': post_data.get('attachments', []),
            'vk_post_id': post_id,
            'source_url': f"https://vk.com/wall{post_data['owner_id']}_{post_data['id']}"
        }
        
        # Add to processed cache
        self.processed_posts_cache.add(post_id)
        
        return processed_post
    
    def _is_post_fresh(self, post_data: Dict[str, Any], theme: str) -> bool:
        """Check if post is recent enough based on theme settings."""
        post_date = datetime.fromtimestamp(post_data['date'])
        max_age = self.theme_settings.get(theme, {}).get('max_age_hours', 24)
        
        age_limit = datetime.utcnow() - timedelta(hours=max_age)
        return post_date > age_limit
    
    def _extract_repost_content(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from reposts (copy_history)."""
        if 'copy_history' in post_data and post_data['copy_history']:
            # Use the original post content
            original = post_data['copy_history'][0]
            post_data = {
                **post_data,
                'text': original.get('text', post_data.get('text', '')),
                'owner_id': original.get('owner_id', post_data['owner_id']),
                'attachments': original.get('attachments', post_data.get('attachments', []))
            }
        return post_data
    
    def _contains_blacklisted_content(self, text: str) -> bool:
        """Check if text contains blacklisted words or phrases."""
        text_lower = text.lower()
        
        for blacklisted_word in self.blacklisted_words:
            if blacklisted_word.lower() in text_lower:
                return True
        
        return False
    
    def _passes_theme_filter(self, post_data: Dict[str, Any], theme: str) -> bool:
        """Apply theme-specific filtering rules."""
        text = post_data.get('text', '')
        attachments = post_data.get('attachments', [])
        
        if theme == 'sosed':
            # Must contain news hashtag
            required_hashtag = self.theme_settings['sosed'].get('require_hashtag')
            if required_hashtag and required_hashtag not in text:
                return False
        
        elif theme in ['kino', 'music']:
            # Must have video or audio attachments
            has_required_media = False
            for att in attachments:
                if (theme == 'kino' and att.get('type') == 'video') or \
                   (theme == 'music' and att.get('type') == 'audio'):
                    has_required_media = True
                    break
            
            if not has_required_media:
                return False
        
        elif theme == 'prikol':
            # Text should be short for funny content
            max_length = self.theme_settings['prikol'].get('max_text_length', 100)
            if len(text) > max_length:
                return False
        
        elif theme == 'novost':
            # News-specific filters
            if not post_data.get('views') and attachments:
                # Remove attachments if no views
                post_data['attachments'] = []
            
            # Check for unwanted links (from legacy code)
            unwanted_domains = ['baltasi', 'kukmor-rt.ru', 'kazved.ru']
            for domain in unwanted_domains:
                if domain in text.lower():
                    return False
        
        return True
    
    def _has_duplicate_media(self, post_data: Dict[str, Any]) -> bool:
        """Check for duplicate images or videos using hashing."""
        attachments = post_data.get('attachments', [])
        
        for att in attachments:
            if att.get('type') == 'photo':
                # Simple hash based on photo sizes (simplified version)
                photo_data = att.get('photo', {})
                sizes = photo_data.get('sizes', [])
                if sizes:
                    # Create a simple hash from the largest image URL
                    largest = max(sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
                    image_hash = hashlib.md5(largest.get('url', '').encode()).hexdigest()
                    
                    if image_hash in self.image_hashes:
                        return True
                    self.image_hashes.add(image_hash)
        
        return False
    
    def _clean_text(self, text: str, theme: str) -> str:
        """Clean and format text based on theme."""
        if not text:
            return ''
        
        # Remove unwanted patterns (from legacy clear_text logic)
        cleaned_text = text
        
        # Theme-specific cleaning
        if theme == 'reklama':
            # Harder cleaning for ads
            # Remove multiple spaces
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            # Remove leading/trailing whitespace
            cleaned_text = cleaned_text.strip()
        
        # Limit text length
        max_length = self.theme_settings.get(theme, {}).get('max_text_length', 4000)
        if len(cleaned_text) > max_length:
            cleaned_text = cleaned_text[:max_length] + '...'
        
        return cleaned_text
    
    def get_regional_hashtags(self, region: str) -> List[str]:
        """Get hashtags for a specific region."""
        hashtags = [f"#{region}"]
        
        if region in self.regions:
            region_name = self.regions[region]
            hashtags.append(f"#{region_name.replace(' ', '_').replace('\'', '')}")
        
        # Add common hashtags
        hashtags.extend(["#новости", "#регион", "#местныеновости"])
        
        return hashtags
    
    async def save_processed_post(self, processed_post: Dict[str, Any]) -> Optional[int]:
        """Save processed post to database."""
        try:
            if not Session:
                logger.warning("SQLAlchemy not available, cannot save post")
                return None
                
            with self.db.get_session() as session:
                db_post = DBPost(
                    title=f"Post from {processed_post['region']}",
                    content=processed_post['text'],
                    region=processed_post['region'],
                    source_collection=processed_post['theme'],
                    vk_group_id=str(processed_post['owner_id']),
                    status='published',
                    created_at=processed_post['date'],
                    post_metadata={
                        'vk_post_id': processed_post['vk_post_id'],
                        'source_url': processed_post['source_url'],
                        'views': processed_post.get('views', {}),
                        'original_text': processed_post.get('original_text', ''),
                        'theme': processed_post['theme']
                    }
                )
                
                session.add(db_post)
                session.commit()
                
                logger.info(f"Saved post {processed_post['vk_post_id']} to database")
                return db_post.id
                
        except Exception as e:
            logger.error(f"Error saving processed post: {e}")
            return None


# Legacy compatibility class
class PostProcessor(EnhancedPostProcessor):
    """Legacy post processor for backward compatibility."""
    
    def __init__(self, config: AppConfig = None):
        super().__init__(config)
        logger.warning("Using legacy PostProcessor class. Consider upgrading to EnhancedPostProcessor.")
