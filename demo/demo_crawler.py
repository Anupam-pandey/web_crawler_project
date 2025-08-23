#!/usr/bin/env python3
"""
Web Crawler API Demo Script

This script demonstrates how to use the Web Crawler API to:
1. Submit a URL for crawling
2. Monitor the crawl progress
3. Retrieve and display the results

Usage:
    python demo_crawler.py [API_URL] [URL_TO_CRAWL]

Example:
    python demo_crawler.py http://web-crawler-env.elasticbeanstalk.com https://www.example.com
"""

import requests
import json
import time
import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

# Initialize rich console
console = Console()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demo script for Web Crawler API")
    parser.add_argument("api_url", nargs="?", 
                        help="Base URL of the deployed API",
                        default="http://localhost:8000")
    parser.add_argument("url_to_crawl", nargs="?",
                        help="URL to crawl and analyze",
                        default="https://www.example.com")
    return parser.parse_args()

def check_api_health(api_url):
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return True, health_data
        else:
            return False, {"error": f"API returned status code {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": f"Connection error: {str(e)}"}

def start_crawl(api_url, url_to_crawl):
    """Start a new crawl job."""
    console.print(f"[bold blue]Starting crawl of[/bold blue] [green]{url_to_crawl}[/green]")
    
    try:
        response = requests.post(
            f"{api_url}/crawl",
            json={"url": url_to_crawl, "respect_robots": True},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        request_id = data["request_id"]
        console.print(f"[bold green]Crawl started![/bold green] Request ID: {request_id}")
        return request_id
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

def poll_results(api_url, request_id):
    """Poll for results until the crawl is complete."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Crawling...", total=None)
        
        while True:
            try:
                response = requests.get(f"{api_url}/result/{request_id}", timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] != "processing":
                    progress.update(task, completed=100)
                    return data
                
                progress.update(task, advance=0)  # Keep the spinner going
                time.sleep(1)
            except requests.exceptions.RequestException as e:
                console.print(f"[bold red]Error polling results:[/bold red] {str(e)}")
                sys.exit(1)

def display_results(data):
    """Display the crawl results in a nicely formatted way."""
    if data["status"] == "completed" and "result" in data:
        result = data["result"]
        metadata = result.get("metadata", {})
        classification = result.get("classification", {})
        
        # Create metadata panel
        metadata_content = [
            f"Title: {metadata.get('title', 'N/A')}",
            f"URL: {metadata.get('url', 'N/A')}",
            f"Domain: {metadata.get('domain', 'N/A')}",
            f"Language: {metadata.get('language', 'N/A')}",
            f"Word Count: {metadata.get('word_count', 'N/A')}"
        ]
        
        if "headings" in metadata:
            headings = metadata["headings"]
            h1_headings = headings.get("h1", [])
            if h1_headings:
                metadata_content.append(f"H1: {h1_headings[0] if h1_headings else 'N/A'}")
        
        metadata_panel = Panel("\n".join(metadata_content), title="Page Metadata", border_style="blue")
        console.print(metadata_panel)
        
        # Create classification panel
        classification_content = [
            f"Page Type: {classification.get('page_type', 'N/A')}"
        ]
        
        # Add categories if available
        categories = classification.get("categories", [])
        if categories:
            classification_content.append("Categories:")
            for category in categories[:3]:  # Show top 3 categories
                name = category.get("name", "unknown")
                confidence = category.get("confidence", 0) * 100
                classification_content.append(f"  - {name} ({confidence:.1f}%)")
        
        # Add topics if available
        topics = classification.get("topics", [])
        if topics:
            classification_content.append("Topics:")
            for topic in topics[:5]:  # Show top 5 topics
                classification_content.append(f"  - {topic}")
        
        classification_panel = Panel("\n".join(classification_content), title="Content Classification", border_style="green")
        console.print(classification_panel)
        
        # Create links table if available
        links = metadata.get("links", [])
        if links:
            table = Table(title="Page Links")
            table.add_column("Text")
            table.add_column("URL")
            table.add_column("Type")
            
            # Show up to 10 links
            for link in links[:10]:
                text = link.get("text", "")
                href = link.get("href", "")
                link_type = "Internal" if link.get("is_internal", False) else "External"
                
                # Truncate long text and URLs
                if len(text) > 30:
                    text = text[:27] + "..."
                if len(href) > 40:
                    href = href[:37] + "..."
                    
                table.add_row(text, href, link_type)
            
            console.print(table)
    
    elif data["status"] == "failed":
        console.print(Panel(f"Error: {data.get('error', 'Unknown error')}", 
                           title="Crawl Failed", border_style="red"))
    else:
        console.print(Panel(f"Unexpected status: {data['status']}", 
                           title="Unexpected Result", border_style="yellow"))

def main():
    """Main function."""
    args = parse_arguments()
    api_url = args.api_url.rstrip('/')
    url_to_crawl = args.url_to_crawl
    
    # Display header
    console.print(Panel("Web Crawler API Demo", style="bold magenta", expand=False))
    
    # Check API health
    console.print("[bold]Checking API health...[/bold]")
    is_healthy, health_data = check_api_health(api_url)
    
    if is_healthy:
        console.print("[bold green]API is healthy![/bold green]")
        components = health_data.get("components", {})
        for component, status in components.items():
            console.print(f"  - {component}: [{'green' if status == 'ok' else 'yellow'}]{status}[/{'green' if status == 'ok' else 'yellow'}]")
        
        # Start the crawl
        request_id = start_crawl(api_url, url_to_crawl)
        
        # Poll for results
        result_data = poll_results(api_url, request_id)
        
        # Display results
        display_results(result_data)
        
    else:
        console.print(f"[bold red]API is not healthy:[/bold red] {health_data.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()