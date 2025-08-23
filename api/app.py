"""
FastAPI application for exposing the web crawler and analyzer as a service.
"""
import os
import time
import random
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import uvicorn
import logging
from typing import Optional, List, Dict, Any

# Import the crawler and analyzer components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler.crawler import WebCrawler
from analyzer.metadata_extractor import MetadataExtractor

# Try importing the classifier with graceful error handling
try:
    from analyzer.classifier import ContentClassifier
    classifier_available = True
except Exception as e:
    logging.warning(f"Error initializing ContentClassifier: {e}")
    classifier_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the crawler and analyzer components
crawler = WebCrawler(
    delay=float(os.getenv("CRAWLER_DELAY", "2.0")),
    user_agent=os.getenv("CRAWLER_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"),
    respect_robots=os.getenv("RESPECT_ROBOTS", "true").lower() == "true",
    browser_emulation=os.getenv("BROWSER_EMULATION", "true").lower() == "true",
    use_fallback=os.getenv("USE_FALLBACK", "true").lower() == "true"
)
metadata_extractor = MetadataExtractor()

# Initialize the content classifier if available
if classifier_available:
    try:
        content_classifier = ContentClassifier()
    except Exception as e:
        logger.warning(f"Failed to initialize ContentClassifier: {e}")
        classifier_available = False
else:
    logger.warning("ContentClassifier is not available - classification features will be disabled")

# Create the FastAPI app
app = FastAPI(
    title="Web Crawler and Analyzer API",
    description="API for crawling websites, extracting metadata, and classifying content",
    version="1.0.0",
)

# Define request and response models
class CrawlRequest(BaseModel):
    url: HttpUrl
    respect_robots: Optional[bool] = True

class CrawlResponse(BaseModel):
    request_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory cache for results (in a real implementation, use Redis or similar)
results_cache = {}

@app.get("/")
async def root():
    """API health check endpoint."""
    return {"status": "OK", "message": "Web Crawler API is running"}

@app.post("/crawl", response_model=CrawlResponse)
async def crawl_url(crawl_request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Crawl a URL, extract metadata, and classify content.
    """
    # Generate a request ID
    request_id = f"req_{int(time.time())}_{hash(crawl_request.url)}"
    
    # Store initial state in cache
    results_cache[request_id] = {
        "status": "processing",
        "url": str(crawl_request.url)
    }
    
    # Run the crawl in the background
    background_tasks.add_task(
        process_url,
        request_id,
        str(crawl_request.url),
        crawl_request.respect_robots
    )
    
    # Return the request ID immediately
    return CrawlResponse(
        request_id=request_id,
        status="processing"
    )

@app.get("/result/{request_id}", response_model=CrawlResponse)
async def get_result(request_id: str):
    """
    Get the result of a previously submitted crawl request.
    """
    if request_id not in results_cache:
        raise HTTPException(status_code=404, detail="Request ID not found")
    
    result = results_cache[request_id]
    
    # Check if processing is complete
    if result["status"] == "processing":
        return CrawlResponse(
            request_id=request_id,
            status="processing"
        )
    elif result["status"] == "failed":
        return CrawlResponse(
            request_id=request_id,
            status="failed",
            error=result.get("error", "Unknown error")
        )
    else:
        return CrawlResponse(
            request_id=request_id,
            status="completed",
            result=result.get("data")
        )

async def process_url(request_id: str, url: str, respect_robots: bool):
    """
    Process a URL by crawling, extracting metadata, and classifying content.
    This function runs as a background task.
    """
    try:
        # Set crawler respect_robots setting
        crawler.respect_robots = respect_robots
        
        # Make up to 3 attempts to crawl the URL with increasing delays
        max_attempts = 3
        attempt = 0
        crawl_result = None
        
        while attempt < max_attempts:
            try:
                # Crawl the URL with exponential backoff
                crawl_result = crawler.crawl(url)
                
                # If successful or got a non-retriable error, break the loop
                if "error" not in crawl_result or "HTTP error: 403" in crawl_result.get("error", ""):
                    break
                    
                # If we got a 500, 502, 503 or similar error, retry
                attempt += 1
                if attempt < max_attempts:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(1, 3)
                    time.sleep(delay)
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}/{max_attempts} crawling {url}: {e}")
                attempt += 1
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)
        
        # Check final result            
        if crawl_result is None or "error" in crawl_result:
            error_msg = crawl_result.get("error", "Unknown error") if crawl_result else "Maximum retry attempts reached"
            results_cache[request_id] = {
                "status": "failed",
                "error": error_msg
            }
            return
        
        # Extract metadata
        metadata = metadata_extractor.extract_metadata(crawl_result["html_content"], url)
        
        # Classify content if the classifier is available
        classification = None
        if classifier_available:
            try:
                classification = content_classifier.classify_page(metadata)
            except Exception as e:
                logger.warning(f"Error classifying content: {e}")
                classification = {
                    "error": "Content classification failed",
                    "page_type": "unknown",
                    "categories": [],
                    "topics": []
                }
        else:
            classification = {
                "note": "Content classification is disabled - NLTK data not available",
                "page_type": "unknown",
                "categories": [],
                "topics": []
            }
        
        # Combine results
        result = {
            "url": url,
            "metadata": metadata,
            "classification": classification,
            "timestamp": time.time()
        }
        
        # Remove the raw HTML to reduce response size
        if "html_content" in crawl_result:
            del crawl_result["html_content"]
            
        # Store the result
        results_cache[request_id] = {
            "status": "completed",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        results_cache[request_id] = {
            "status": "failed",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    components = {
        "crawler": "ok",
        "metadata_extractor": "ok",
        "content_classifier": "ok" if classifier_available else "disabled"
    }
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "components": components,
        "notes": [] if classifier_available else ["NLTK data not available - classification features limited"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
