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

## API Documentation

Once running, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

### Cloud Deployment

AWS CloudFormation template is available in `deployment/aws.yml`.

## Design Documentation

- **Design Document**: See `docs/design_doc.md` for the system architecture and scaling design
- **Implementation Plan**: See `docs/implementation_plan.md` for the phased approach to production

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.