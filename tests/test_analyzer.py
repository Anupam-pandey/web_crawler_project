"""Test the analyzer components."""
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.metadata_extractor import MetadataExtractor

def test_metadata_extraction_basic_html():
    """Test basic metadata extraction from HTML."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="description" content="Test description">
        <meta name="keywords" content="test,keywords">
        <title>Test Page</title>
        <link rel="canonical" href="https://example.com/test" />
    </head>
    <body>
        <h1>Main Heading</h1>
        <p>This is a test paragraph with some text.</p>
        <a href="https://example.com/link1">Link 1</a>
        <a href="https://external.com/link2">Link 2</a>
    </body>
    </html>
    """
    
    extractor = MetadataExtractor()
    metadata = extractor.extract_metadata(html_content, "https://example.com/test-page")
    
    assert metadata is not None
    assert metadata["title"] == "Test Page"
    assert metadata["description"] == "Test description"
    assert metadata["canonical_url"] == "https://example.com/test"
    assert len(metadata["headings"]["h1"]) == 1
    assert metadata["headings"]["h1"][0] == "Main Heading"
    
    # Test links
    assert len(metadata["links"]) == 2
    assert any(link["href"] == "https://example.com/link1" for link in metadata["links"])
    assert any(link["href"] == "https://external.com/link2" for link in metadata["links"])

def test_metadata_extraction_empty_html():
    """Test metadata extraction from empty HTML."""
    html_content = "<html><head></head><body></body></html>"
    
    extractor = MetadataExtractor()
    metadata = extractor.extract_metadata(html_content, "https://example.com/empty")
    
    assert metadata is not None
    assert metadata["title"] is None or metadata["title"] == ""
    assert metadata["description"] is None or metadata["description"] == ""
    assert "headings" in metadata
    assert "h1" in metadata["headings"]
    assert len(metadata["headings"]["h1"]) == 0
    assert "links" in metadata
    assert len(metadata["links"]) == 0

def test_metadata_extraction_with_malformed_html():
    """Test metadata extraction from malformed HTML."""
    html_content = """<html><head><title>Broken Page</title></
    <body><h1>Heading
    <p>Paragraph without closing tag
    <a href=no-quotes>Bad link</a>
    </html>
    """
    
    extractor = MetadataExtractor()
    metadata = extractor.extract_metadata(html_content, "https://example.com/broken")
    
    # Even with malformed HTML, we should get a result
    assert metadata is not None
    assert metadata["title"] == "Broken Page"
    
    # BeautifulSoup should still find the heading and link
    assert len(metadata["headings"]["h1"]) > 0
    assert "Bad link" in [link.get("text", "") for link in metadata["links"]]

if __name__ == "__main__":
    test_metadata_extraction_basic_html()
    test_metadata_extraction_empty_html()
    test_metadata_extraction_with_malformed_html()
