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
import asyncio
import importlib
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebCrawler:
    """
    A web crawler that respects robots.txt and extracts page content.
    Has fallback methods using browser automation for sites with anti-crawler measures.
    """
    
    def __init__(self, delay=1.0, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36", respect_robots=True, browser_emulation=True, use_fallback=True):
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
        self.browser_emulation = browser_emulation
        self.use_fallback = use_fallback
        self.domain_last_accessed = {}
        self.robots_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        self.robots_cache = {}
        self._playwright_available = self._check_module_available('playwright')
        
        # List of common user agents to rotate through when browser_emulation is enabled
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/99.0.1150.36 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'
        ]
        
        # Common referrer URLs to use when browser_emulation is enabled
        self.referrers = [
            'https://www.google.com/',
            'https://www.google.com/search?q=product+reviews',
            'https://www.bing.com/search?q=product+information',
            'https://search.yahoo.com/search?p=product+details',
            'https://duckduckgo.com/?q=product+specs'
        ]
        
        # Default request headers
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",  # Do Not Track request header
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
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
            response = requests.get(robots_url, headers=self.headers, timeout=15)
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
            # Add jitter to requests to avoid detection
            jitter_delay = random.uniform(0.5, 2.5)
            time.sleep(jitter_delay)
            
            # Create a session to manage cookies and add retry mechanism
            session = requests.Session()
            
            # Clone the headers and customize for this request
            current_headers = self.headers.copy()
            
            # Set headers to emulate a browser if enabled
            if self.browser_emulation:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                
                # Rotate user agents
                current_headers['User-Agent'] = random.choice(self.user_agents)
                
                # Use a random referrer with a search query related to the domain
                base_referrer = random.choice(self.referrers)
                keywords = domain.split('.')
                if len(keywords) > 1 and keywords[0] not in ['www', 'blog']:
                    search_term = keywords[0]
                    current_headers['Referer'] = f"{base_referrer}{search_term}"
                else:
                    current_headers['Referer'] = base_referrer
                
                # Add common browser cookies for consent etc.
                current_headers['Cookie'] = 'consent=true; notice_behavior=implied,us'
                
                # Add cache control headers to simulate fresh browser request
                current_headers['Cache-Control'] = 'max-age=0'
                current_headers['Sec-Ch-Ua'] = '"Chromium";v="112", "Google Chrome";v="112"'
                
            # Send the request with session
            logger.info(f"Crawling URL: {url}")
            response = session.get(
                url, 
                headers=current_headers, 
                timeout=30,
                allow_redirects=True
            )
            
            # Check if request was successful
            if response.status_code != 200:
                return {
                    "error": f"HTTP error: {response.status_code}",
                    "url": url,
                    "response_headers": dict(response.headers)
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
            
            # Try fallback methods if regular request failed and fallbacks are enabled
            if self.use_fallback:
                logger.info(f"Trying fallback methods for {url} after RequestException")
                try:
                    # Try with a headless browser if available
                    if self._playwright_available:
                        return asyncio.run(self._fallback_playwright(url))
                    else:
                        logger.warning("No fallback browser libraries available")
                except Exception as fb_error:
                    logger.error(f"Fallback method also failed for {url}: {fb_error}")
            
            return {
                "error": str(e),
                "url": url
            }
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {e}")
            
            # Try fallback methods if regular request failed and fallbacks are enabled
            if self.use_fallback:
                logger.info(f"Trying fallback methods for {url}")
                try:
                    # Try with a headless browser if available
                    if self._playwright_available:
                        return asyncio.run(self._fallback_playwright(url))
                    else:
                        logger.warning("No fallback browser libraries available")
                except Exception as fb_error:
                    logger.error(f"Fallback method also failed for {url}: {fb_error}")
            
            return {
                "error": str(e),
                "url": url
            }

    def _check_module_available(self, module_name):
        """Check if a Python module is available to import"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    async def _fallback_playwright(self, url):
        """Use Playwright as a fallback method to fetch content from anti-bot sites"""
        try:
            # Import Playwright modules
            from playwright.async_api import async_playwright
            
            logger.info(f"Using Playwright async API to fetch {url}")
            
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            
            # Create a context with stealth options
            context = await browser.new_context(
                user_agent=random.choice(self.user_agents) if self.browser_emulation else self.user_agent,
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1
            )
            
            # Add some randomization to appear more human-like
            page = await context.new_page()
            await page.goto("https://www.google.com")
            await page.wait_for_timeout(random.randint(500, 1500))
            
            # Go to the actual target URL
            response = await page.goto(url, timeout=30000)
            
            if response.status != 200:
                await browser.close()
                await playwright.stop()
                return {
                    "error": f"HTTP error: {response.status}",
                    "url": url
                }
            
            # Wait for content to fully load
            await page.wait_for_load_state("networkidle")
            
            # Extract content
            html_content = await page.content()
            await browser.close()
            await playwright.stop()
            
            return {
                "url": url,
                "status_code": 200,
                "content_type": "text/html",
                "html_content": html_content,
                "headers": {"Content-Type": "text/html"},
                "timestamp": time.time()
            }
                
        except Exception as e:
            logger.error(f"Playwright fallback failed for {url}: {e}")
            return {"error": f"Playwright fallback failed: {str(e)}", "url": url}
    

# For testing
if __name__ == "__main__":
    crawler = WebCrawler(delay=2.0)
    result = crawler.crawl("https://www.example.com")
    print(f"Status code: {result.get('status_code')}")
    print(f"Content length: {len(result.get('html_content', ''))}")
