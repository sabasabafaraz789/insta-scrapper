from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Optional


class InstagramScraper:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.data = {}

    def extract_profile_info(self) -> Dict:
        """Extract basic profile information"""
        profile = {}
        
        # Username
        username_elem = self.soup.find('h2', string=re.compile(r'.*'))
        if username_elem:
            profile['username'] = username_elem.get_text().strip()
        
        # Full name
        full_name_elem = self.soup.find('span', string=re.compile(r'^[A-Z][a-z]+'))
        if full_name_elem:
            profile['full_name'] = full_name_elem.get_text().strip()
        
        # Bio
        bio_elem = self.soup.find('span', class_=re.compile(r'_aaco.*_aacu.*_aacx.*_aad7.*_aade'))
        if bio_elem:
            profile['bio'] = bio_elem.get_text().strip()
        
        # Website
        website_elem = self.soup.find('a', href=re.compile(r'https?://'))
        if website_elem and 'http' in website_elem.get_text():
            profile['website'] = website_elem.get_text().strip()
        
        # Profile picture
        profile_img = self.soup.find('img', alt=re.compile(r".*profile picture"))
        if profile_img and profile_img.get('src'):
            profile['profile_picture_url'] = profile_img['src']
        
        # Verification status
        verified_svg = self.soup.find('svg', {'aria-label': 'Verified'})
        profile['is_verified'] = verified_svg is not None
        
        return profile     
    
    
    
    def extract_profile_stats(self) -> Dict:
        """Extract posts, followers, following counts"""
        stats = {}
        
        # Find all stat elements
        stat_elements = self.soup.find_all('span', class_=re.compile(r'html-span.*xdj266r.*x14z9mp'))
        
        for elem in stat_elements:
            text = elem.get_text().strip()
            parent_text = elem.find_parent().get_text() if elem.find_parent() else ""
            
            # Posts count
            if 'posts' in parent_text.lower() and text.replace(',', '').replace('.', '').isdigit():
                stats['posts'] = self._parse_count(text)
            
            # Followers count
            elif 'followers' in parent_text.lower():
                stats['followers'] = self._parse_count(text)
            
            # Following count
            elif 'following' in parent_text.lower():
                stats['following'] = self._parse_count(text)
        
        # Alternative method
        if not stats:
            stat_spans = self.soup.find_all('span', string=re.compile(r'\d+[MK]?'))
            for span in stat_spans:
                parent_text = span.find_parent().get_text() if span.find_parent() else ""
                text = span.get_text().strip()
                
                if 'post' in parent_text.lower():
                    stats['posts'] = self._parse_count(text)
                elif 'follower' in parent_text.lower():
                    stats['followers'] = self._parse_count(text)
                elif 'following' in parent_text.lower():
                    stats['following'] = self._parse_count(text)
        
        return stats
    
    def _parse_count(self, count_str: str) -> int:
        """Convert count string like '391M' to integer"""
        count_str = count_str.upper().replace(',', '')
        
        if 'M' in count_str:
            return int(float(count_str.replace('M', '')) * 1000000)
        elif 'K' in count_str:
            return int(float(count_str.replace('K', '')) * 1000)
        else:
            try:
                return int(count_str)
            except:
                return 0
    
    def extract_posts(self) -> List[Dict]:
        """Extract post information from Instagram profile"""
        posts = []
        
        # Find the main posts container
        posts_container = self.soup.find('div', class_='xg7h5cd x1n2onr6')
        if not posts_container:
            return posts
        
        # Find all individual post containers
        post_containers = posts_container.find_all('div', class_='x1lliihq x1n2onr6 xh8yej3 x4gyw5p x14z9mp xhe4ym4 xaudc5v x1j53mea')
        
        for container in post_containers:
            post = {}
            
            # Find the post link
            post_link = container.find('a', href=re.compile(r'/.+/.*/'))
            if not post_link or not post_link.get('href'):
                continue
                
            # Post URL - concatenate with base URL
            post['url'] = "https://www.instagram.com" + post_link['href']
            
            # Extract post ID from URL
            post_id_match = re.search(r'/([A-Za-z0-9_-]+)/?$', post_link['href'])
            if post_id_match:
                post['post_id'] = post_id_match.group(1)
            
            # Media content
            img = post_link.find('img')
            if img:
                if img.get('src'):
                    post['thumbnail_url'] = img['src']
                if img.get('alt'):
                    post['caption'] = img['alt']
            
            # Media type detection
            parent_html = str(container)
            if 'reel' in post.get('url', '').lower():
                post['media_type'] = 'reel'
            elif 'clip' in parent_html.lower():
                post['media_type'] = 'reel'
            elif 'carousel' in parent_html.lower():
                post['media_type'] = 'carousel'
            else:
                post['media_type'] = 'image'
            
            # Pinned post detection
            if 'pinned post icon' in parent_html.lower():
                post['is_pinned'] = True
            else:
                post['is_pinned'] = False
            
            # Only add if we have basic info
            if post.get('url'):
                posts.append(post)
        
        return posts
    
    def extract_highlights(self) -> List[Dict]:
        """Extract story highlights from the specific section structure"""
        highlights = []
        
        # Method 1: Look for the specific highlight section structure
        highlight_section = self.soup.find('section', class_=re.compile(r'.*xcrlgei.*x1682tcd.*xtyw845'))
        
        if highlight_section:
            # Find all highlight items with class "_acaz"
            highlight_items = highlight_section.find_all('li', class_='_acaz')
            
            for item in highlight_items:
                highlight = {}
                
                # Extract highlight title
                title_span = item.find('span', class_=re.compile(r'x1lliihq.*x193iq5w.*x6ikm8r.*x10wlt62'))
                if title_span:
                    highlight['title'] = title_span.get_text().strip()
                
                # Extract cover image URL
                img = item.find('img', alt=re.compile(r".*highlight story picture"))
                if img and img.get('src'):
                    highlight['cover_url'] = img['src']
                    if img.get('alt'):
                        highlight['alt_text'] = img['alt']
                
                # Extract additional metadata
                canvas = item.find('canvas')
                if canvas:
                    highlight['has_canvas'] = True
                
                # Extract positioning info
                style = item.get('style', '')
                transform_match = re.search(r'translateX\((\d+)px\)', style)
                if transform_match:
                    highlight['position'] = int(transform_match.group(1))
                
                if highlight.get('title'):  # Only add if we have a title
                    highlights.append(highlight)
        
        # Method 2: Alternative approach looking for highlight containers
        if not highlights:
            highlight_containers = self.soup.find_all('div', class_=re.compile(r'.*x5lhr3w.*'))  # Common highlight container class
            
            for container in highlight_containers:
                highlight = {}
                
                # Title
                title_elem = container.find('span', class_=re.compile(r'.*x1lliihq.*x193iq5w.*'))
                if title_elem:
                    highlight['title'] = title_elem.get_text().strip()
                
                # Cover image
                img = container.find('img')
                if img and img.get('src'):
                    highlight['cover_url'] = img['src']
                    if img.get('alt'):
                        highlight['alt_text'] = img['alt']
                
                if highlight:  # Only add if we have data
                    highlights.append(highlight)
        
        return highlights
    
    def extract_all_data(self) -> Dict:
        """Extract all available data"""
        self.data = {
            'profile': self.extract_profile_info(),
            'stats': self.extract_profile_stats(),
            'posts': self.extract_posts(),
            'highlights': self.extract_highlights()
        }
        return self.data
    
    def to_json(self) -> str:
        """Return data as JSON string"""
        if not self.data:
            self.extract_all_data()
        return json.dumps(self.data, indent=2, ensure_ascii=False)



