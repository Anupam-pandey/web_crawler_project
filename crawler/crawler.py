"""
Web Crawler module for extracting web page content.
"""
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin
import re
import time
import random
from pathlib import Path
import os
import robotexclusionrulesparser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebCrawler:
    """
    A web crawler that respects robots.txt and extracts page content.
    """
    
    def __init__(self, delay=1.0, user_agent="SEOCrawlerBot/1.0", respect_robots=True):
        """
        Initialize the crawler with configurable parameters.
        
        Args:
            delay (float): Delay between requests to the same domain in seconds
            user_agent (str): User agent string to identify the crawler
            respect_robots (bool): Whether to respect robots.txt rules
        """
        self.delay = delay
        self.user_agent = user_agent
        self.respect_robots = respect_robots
        self.domain_last_accessed = {}
        self.robots_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        self.robots_cache = {}
        
        # Default request headers
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",  # Do Not Track request header
        }
    
    def _get_robots_parser(self, url):
        """Get and parse robots.txt for the given URL's domain."""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check if we already parsed robots.txt for this domain
        if base_url in self.robots_cache:
            return self.robots_cache[base_url]
        
        # Fetch and parse robots.txt
        robots_url = f"{base_url}/robots.txt"
        try:
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.robots_parser.parse(response.text)
            else:
                # If no robots.txt or error, assume everything is allowed
                self.robots_parser.parse("")
                
            # Cache the parser for this domain
            self.robots_cache[base_url] = self.robots_parser
            return self.robots_parser
            
        except Exception as e:
            logger.warning(f"Error fetching robots.txt for {base_url}: {e}")
            # If error, assume everything is allowed
            self.robots_parser.parse("")
            self.robots_cache[base_url] = self.robots_parser
            return self.robots_parser
    
    def _is_crawlable(self, url):
        """Check if the URL is allowed to be crawled according to robots.txt."""
        if not self.respect_robots:
            return True
            
        parser = self._get_robots_parser(url)
        return parser.is_allowed(self.user_agent, url)
    
    def _respect_crawl_delay(self, url):
        """Respect the crawl delay for a specific domain."""
        domain = urlparse(url).netloc
        
        # Check if we've accessed this domain before
        if domain in self.domain_last_accessed:
            last_time = self.domain_last_accessed[domain]
            sleep_time = self.delay - (time.time() - last_time)
            
            # If we need to wait, do so
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Update the last access time
        self.domain_last_accessed[domain] = time.time()
    
    def crawl(self, url):
        """
        Crawl a URL and extract its content.
        
        Args:
            url (str): The URL to crawl
            
        Returns:
            dict: A dictionary containing the raw HTML and other metadata
        """
        # Check if URL is allowed to be crawled
        if not self._is_crawlable(url):
            logger.warning(f"URL {url} is disallowed by robots.txt")
            return {"error": "URL disallowed by robots.txt"}
        
        # Respect crawl delay
        self._respect_crawl_delay(url)
        
        try:
            # Send the request
            logger.info(f"Crawling URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            # Check if request was successful
            if response.status_code != 200:
                return {
                    "error": f"HTTP error: {response.status_code}",
                    "url": url
                }
                
            # Get content type from headers
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Only process HTML content
            if 'text/html' not in content_type:
                return {
                    "error": f"Not HTML content: {content_type}",
                    "url": url
                }
                
            # Return the raw content and metadata
            result = {
                "url": url,
                "status_code": response.status_code,
                "content_type": content_type,
                "html_content": response.text,
                "headers": dict(response.headers),
                "timestamp": time.time()
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return {
                "error": str(e),
                "url": url
            }
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {e}")
            return {
                "error": str(e),
                "url": url
            }

# For testing
if __name__ == "__main__":
    crawler = WebCrawler(delay=2.0)
    result = crawler.crawl("https://www.example.com")
    print(f"Status code: {result.get('status_code')}")
    print(f"Content length: {len(result.get('html_content', ''))}")