"""Test the web crawler functionality."""
import asyncio
import os
import sys
import pytest

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.crawler import WebCrawler

def test_crawler_initialization():
    """Test that the crawler initializes with correct default parameters"""
    crawler = WebCrawler()
    assert crawler.delay == 1.0
    assert crawler.respect_robots == True
    assert crawler.browser_emulation == True
    assert crawler.use_fallback == True
    
    # Test with custom parameters
    custom_crawler = WebCrawler(delay=2.0, respect_robots=False, browser_emulation=False, use_fallback=False)
    assert custom_crawler.delay == 2.0
    assert custom_crawler.respect_robots == False
    assert custom_crawler.browser_emulation == False
    assert custom_crawler.use_fallback == False

def test_crawl_example_site():
    """Test crawling a simple example site"""
    crawler = WebCrawler()
    result = crawler.crawl("https://example.com")
    
    assert result is not None
    assert "status_code" in result
    assert result["status_code"] == 200
    assert "html_content" in result
    assert "Example Domain" in result["html_content"]

def test_nonexistent_site():
    """Test crawling a non-existent site"""
    crawler = WebCrawler()
    result = crawler.crawl("https://thissitedoesnotexist12345.com")
    
    assert "error" in result
    # The error could be from regular request or from Playwright fallback
    assert "Playwright fallback failed" in result["error"] or "Request error" in result["error"] or "Failed to establish" in result["error"]

def test_robots_txt_compliance():
    """Test that the crawler respects robots.txt"""
    # Create a crawler that respects robots.txt
    crawler_respectful = WebCrawler(respect_robots=True)
    
    # Create a crawler that ignores robots.txt
    crawler_disrespectful = WebCrawler(respect_robots=False)
    
    # Choose a URL that's commonly disallowed in robots.txt
    test_url = "https://www.google.com/search"
    
    # Test the respectful crawler
    respectful_result = crawler_respectful.crawl(test_url)
    assert "error" in respectful_result
    assert "disallowed by robots.txt" in respectful_result["error"]
    
    # Test the disrespectful crawler
    disrespectful_result = crawler_disrespectful.crawl(test_url)
    # May still fail for other reasons but not robots.txt
    if "error" in disrespectful_result:
        assert "disallowed by robots.txt" not in disrespectful_result["error"]

if __name__ == "__main__":
    test_crawler_initialization()
    test_crawl_example_site()
    test_nonexistent_site()
    test_robots_txt_compliance()
