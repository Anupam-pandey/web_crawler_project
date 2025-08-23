# Web Crawler and Content Analyzer

A scalable web crawler system designed to extract metadata, classify content, and analyze topics from web pages. This project serves as both a proof of concept and a foundation for a web-scale crawling system.

## Features

- **Polite Web Crawling**: Respects robots.txt and implements configurable crawl delays
- **Metadata Extraction**: Extracts titles, descriptions, headings, links, and other metadata
- **Content Classification**: Identifies page types and categories
- **Topic Extraction**: Determines relevant topics from page content
- **REST API**: Exposes crawling and analysis capabilities as a service
- **Cloud Deployment**: Ready to deploy on AWS with scalable infrastructure
- **Demo Script**: Includes a user-friendly demonstration script

## Architecture

The system consists of several components:

1. **Crawler**: Fetches web pages while respecting robots.txt rules
2. **Metadata Extractor**: Extracts structured data from HTML content
3. **Content Classifier**: Categorizes pages and identifies topics
4. **API Layer**: Provides RESTful access to the system's capabilities

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd web_crawler_project
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application Locally

Start the API server:

```
uvicorn api.app:app --reload
```

The API will be available at http://localhost:8000

### Running the Demo Script

We've included a demonstration script that showcases the functionality:

```
# Install demo dependencies
pip install rich requests

# Run the demo against a local server
python demo/demo_crawler.py http://localhost:8000 https://www.example.com

# Or against a deployed instance
python demo/demo_crawler.py https://your-deployed-url.com https://www.example.com
```

### Cloud Deployment

This project is configured for easy deployment to Render, which offers a reliable free tier:

- **Render Deployment**: See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for step-by-step instructions

The Render deployment is ideal for demo purposes because:
- Free tier with 750 hours/month (enough for continuous operation)
- No credit card required
- Provides a public HTTPS URL for sharing with examiners
- Automatic deployment from GitHub
- Built-in logs and monitoring


**Important Note**: The free instance will spin down with inactivity, which can delay requests by 50 seconds or more. The first request after a period of inactivity will take longer as the instance spins up.

## Usage Examples

### Crawl a URL

```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "respect_robots": true}'
```

### Check Crawl Status

```bash
curl "http://localhost:8000/result/req_1234567890"
```

### Test Assignment URLs

Here are the curl commands for the specific test URLs mentioned in the assignment:

```bash
# Amazon product URL
curl -X POST "https://web-crawler-project-r685.onrender.com/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster", "respect_robots": true}'

# REI blog URL
curl -X POST "https://web-crawler-project-r685.onrender.com/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/", "respect_robots": true}'

# CNN article URL
curl -X POST "https://web-crawler-project-r685.onrender.com/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/", "respect_robots": true}'
```

To check the results (replace req_id with the request ID returned from the above commands):

```bash
curl "https://web-crawler-project-r685.onrender.com/result/req_id"
```

Note: Commercial websites may return different results when crawled from cloud environments versus local environments due to anti-bot protections.

### Recommended Test URLs

These URLs generally allow crawling and work well with our system:

```
# Simple websites
https://example.com/
https://httpbin.org/html

# Documentation sites
https://docs.python.org/3/
https://en.wikipedia.org/wiki/Web_crawler

# Open source project sites
https://www.python.org/

# Assignment Test URLs
http://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster
http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/
http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/
```

**Note**: Some websites implement strict access controls that may prevent successful crawling. For example, Amazon's response differs based on the origin of the request - local development environments typically receive more complete data compared to cloud environments (like Render) which may be detected as potential bots and served restricted content. This is due to IP-based bot detection systems that view cloud provider IPs with higher suspicion.

## API Documentation

### Local Development
When running locally, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Deployed Application
For the deployed Render application, access the API documentation at:

- Swagger UI: https://web-crawler-project-r685.onrender.com/docs
- ReDoc: https://web-crawler-project-r685.onrender.com/redoc

These interactive documentation interfaces allow you to test the API directly from your browser without using curl commands.

## Deployment

### Docker

Build the Docker image:

```
docker build -t web-crawler .
```

Run the container:

```
docker run -p 8000:8000 web-crawler
```

## Design Documentation

- **Part 2 - Scaled Crawler Design**: See `docs/scaled_crawler_design.md` for detailed billion-scale URL processing architecture with optimizations for cost, reliability, performance, and scale
- **Part 3 - Proof of Concept Plan**: See `docs/proof_of_concept_plan.md` for implementation plan with anti-bot challenges, potential blockers, and implementation schedules
