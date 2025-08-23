# Web Crawler API Demo

This directory contains a demonstration script to showcase the functionality of the Web Crawler API.

## Prerequisites

Install the required dependencies for the demo script:

```bash
pip install requests rich
```

## Usage

The demo script allows you to test the crawler API against any URL. It connects to your deployed API and displays the results in a user-friendly format.

### Basic Usage

```bash
python demo_crawler.py [API_URL] [URL_TO_CRAWL]
```

For example:

```bash
# Test against the deployed API
python demo_crawler.py https://web-crawler-demo.onrender.com https://www.example.com

# Test against a local development server
python demo_crawler.py http://localhost:8000 https://www.amazon.com
```

### Features

The demo script demonstrates several key features of the Web Crawler API:

1. **Health check**: Verifies the API is operational
2. **Crawl submission**: Submits a URL for crawling
3. **Progress tracking**: Monitors the crawl job progress
4. **Result display**: Shows the crawled data in a formatted way, including:
   - Page metadata (title, description, word count)
   - Content classification (page type, categories, topics)
   - Links found on the page

## Example Output

When running the demo script, you'll see output similar to this:

```
┏━━━━━━━━━━━━━━━━━━━━━┓
┃ Web Crawler API Demo ┃
┗━━━━━━━━━━━━━━━━━━━━━┛

Checking API health...
API is healthy!
  - crawler: ok
  - metadata_extractor: ok
  - content_classifier: ok

Starting crawl of https://www.example.com
Crawl started! Request ID: req_1682945028_1234567890

⠋ Crawling... 

┏━━━━━━━━━━━━━━━━━┓
┃ Page Metadata   ┃
┗━━━━━━━━━━━━━━━━━┛
Title: Example Domain
URL: https://www.example.com
Domain: example.com
Language: en
Word Count: 27
H1: Example Domain

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ Content Classification ┃
┗━━━━━━━━━━━━━━━━━━━━━┛
Page Type: generic
Categories:
  - corporate (60.0%)
Topics:
  - example
  - domain
  - information
  - website
```
