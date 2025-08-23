"""
Metadata Extractor module for extracting useful metadata from web pages.
"""
import re
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetadataExtractor:
    """
    Extracts metadata from HTML content including title, description, body text,
    headings, and other SEO-relevant elements.
    """
    
    def __init__(self):
        """Initialize the metadata extractor."""
        pass
    
    def extract_metadata(self, html_content, url):
        """
        Extract metadata from HTML content.
        
        Args:
            html_content (str): The raw HTML content
            url (str): The URL of the page
            
        Returns:
            dict: Extracted metadata
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic metadata
            metadata = {
                "url": url,
                "domain": urlparse(url).netloc,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "canonical_url": self._extract_canonical(soup, url),
                "language": self._extract_language(soup),
                "headings": self._extract_headings(soup),
                "text_content": self._extract_main_content(soup),
                "word_count": 0,  # Will be calculated
                "links": self._extract_links(soup, url),
                "images": self._extract_images(soup, url),
                "structured_data": self._extract_structured_data(soup),
                "meta_tags": self._extract_meta_tags(soup),
            }
            
            # Calculate word count
            if metadata["text_content"]:
                metadata["word_count"] = len(metadata["text_content"].split())
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {
                "error": str(e),
                "url": url
            }
    
    def _extract_title(self, soup):
        """Extract the page title."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _extract_description(self, soup):
        """Extract the meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.has_attr('content'):
            return meta_desc['content'].strip()
        return None
    
    def _extract_canonical(self, soup, default_url):
        """Extract the canonical URL."""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical and canonical.has_attr('href'):
            return canonical['href']
        return default_url
    
    def _extract_language(self, soup):
        """Extract the page language."""
        # Check html tag
        html_tag = soup.find('html')
        if html_tag and html_tag.has_attr('lang'):
            return html_tag['lang']
        
        # Check meta tags
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang and meta_lang.has_attr('content'):
            return meta_lang['content']
            
        return None
    
    def _extract_headings(self, soup):
        """Extract all headings (h1-h6) from the page."""
        headings = {}
        
        for level in range(1, 7):
            tag = f'h{level}'
            heading_tags = soup.find_all(tag)
            headings[tag] = [heading.get_text().strip() for heading in heading_tags]
            
        return headings
    
    def _extract_main_content(self, soup):
        """Extract the main textual content from the page."""
        # Try to find content in main content tags
        for tag in ['main', 'article', 'section', '[role=main]']:
            content = soup.select(tag)
            if content:
                return ' '.join([el.get_text().strip() for el in content])
        
        # If no main content found, extract from body but remove navigation, header, footer, etc.
        for el in soup.select('nav, header, footer, aside, style, script, [role=banner], [role=navigation], [role=complementary]'):
            el.extract()
            
        body = soup.find('body')
        if body:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', body.get_text().strip())
            return text
            
        return None
    
    def _extract_links(self, soup, base_url):
        """Extract all links from the page."""
        links = []
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                href = link['href']
                text = link.get_text().strip()
                links.append({
                    'href': href,
                    'text': text,
                    'is_internal': not href.startswith('http') or urlparse(base_url).netloc in href
                })
        return links
    
    def _extract_images(self, soup, base_url):
        """Extract all images from the page."""
        images = []
        for img in soup.find_all('img'):
            image_data = {}
            
            if img.has_attr('src'):
                image_data['src'] = img['src']
                
            if img.has_attr('alt'):
                image_data['alt'] = img['alt']
                
            if img.has_attr('title'):
                image_data['title'] = img['title']
                
            images.append(image_data)
            
        return images
    
    def _extract_structured_data(self, soup):
        """Extract structured data (JSON-LD) from the page."""
        structured_data = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, TypeError):
                pass
                
        return structured_data
    
    def _extract_meta_tags(self, soup):
        """Extract all meta tags from the page."""
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            if meta.has_attr('name') and meta.has_attr('content'):
                meta_tags[meta['name']] = meta['content']
            elif meta.has_attr('property') and meta.has_attr('content'):
                meta_tags[meta['property']] = meta['content']
                
        return meta_tags

# For testing
if __name__ == "__main__":
    from crawler import WebCrawler
    
    crawler = WebCrawler()
    extractor = MetadataExtractor()
    
    url = "https://www.example.com"
    result = crawler.crawl(url)
    
    if 'html_content' in result:
        metadata = extractor.extract_metadata(result['html_content'], url)
        print(f"Title: {metadata.get('title')}")
        print(f"Description: {metadata.get('description')}")
        print(f"Word count: {metadata.get('word_count')}")