"""
Content Classifier module for classifying web pages and extracting topics.
"""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download necessary NLTK resources
def ensure_nltk_data():
    required_packages = ['punkt', 'stopwords', 'wordnet']
    missing_packages = []
    
    # Check which packages are already downloaded
    for package in required_packages:
        try:
            if package == 'punkt':
                nltk.data.find('tokenizers/punkt')
            else:
                nltk.data.find(f'corpora/{package}')
        except LookupError:
            missing_packages.append(package)
    
    # Try to download missing packages
    if missing_packages:
        logger.info(f"Attempting to download required NLTK data: {', '.join(missing_packages)}")
        try:
            for package in missing_packages:
                nltk.download(package)
            logger.info("Successfully downloaded all required NLTK data")
        except Exception as e:
            logger.warning(f"Failed to download NLTK data automatically: {e}")
            logger.warning("You need to download NLTK data manually. Run the following commands in Python:")
            logger.warning("import nltk")
            for package in missing_packages:
                logger.warning(f"nltk.download('{package}')")
            logger.warning("Alternatively, you can create a fallback using simple methods for now")

# Initialize NLTK resources
ensure_nltk_data()

class ContentClassifier:
    """
    Classifies web pages based on their content and extracts relevant topics.
    """
    
    def __init__(self):
        """Initialize the content classifier."""
        # Try to use NLTK resources, fall back to basic implementation if not available
        try:
            self.stop_words = set(stopwords.words('english'))
            self.use_nltk = True
        except Exception:
            # Fallback to a basic set of stop words if NLTK data is not available
            logger.warning("Using fallback stop words list")
            self.stop_words = {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
                'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
                'to', 'from', 'in', 'on', 'by', 'with', 'at', 'into'
            }
            self.use_nltk = False
            
        try:
            self.lemmatizer = WordNetLemmatizer()
        except Exception:
            # We'll just use the words as-is if lemmatization is not available
            self.lemmatizer = None
            
        # Pre-defined categories with associated keywords
        self.categories = {
            'e-commerce': ['product', 'buy', 'shop', 'store', 'price', 'cart', 'purchase', 'shipping', 'offer', 'discount', 'deal'],
            'news': ['news', 'report', 'article', 'journalist', 'breaking', 'coverage', 'story', 'reported', 'according', 'sources'],
            'blog': ['blog', 'post', 'author', 'opinion', 'comment', 'thoughts', 'personal', 'experience', 'perspective'],
            'corporate': ['company', 'business', 'corporate', 'enterprise', 'industry', 'service', 'solution', 'professional', 'client'],
            'educational': ['learn', 'course', 'education', 'student', 'school', 'university', 'academic', 'study', 'training', 'teaching'],
            'technology': ['tech', 'technology', 'software', 'hardware', 'digital', 'app', 'application', 'device', 'platform', 'system']
        }
        
    def preprocess_text(self, text):
        """Preprocess the text for analysis."""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        if self.use_nltk:
            try:
                tokens = word_tokenize(text)
            except Exception:
                # Fallback tokenization - simple split by whitespace
                tokens = text.split()
        else:
            tokens = text.split()
        
        # Remove stopwords and lemmatize
        if self.lemmatizer:
            try:
                filtered_tokens = [
                    self.lemmatizer.lemmatize(token) 
                    for token in tokens 
                    if token not in self.stop_words and len(token) > 1
                ]
            except Exception:
                filtered_tokens = [
                    token for token in tokens 
                    if token not in self.stop_words and len(token) > 1
                ]
        else:
            filtered_tokens = [
                token for token in tokens 
                if token not in self.stop_words and len(token) > 1
            ]
        
        return " ".join(filtered_tokens)
    
    def classify_page(self, metadata):
        """
        Classify the page based on its content.
        
        Args:
            metadata (dict): The extracted metadata from the page
            
        Returns:
            dict: Classification results and extracted topics
        """
        try:
            # Combine title, description, and content
            combined_text = ""
            if metadata.get('title'):
                combined_text += f"{metadata['title']} "
                
            if metadata.get('description'):
                combined_text += f"{metadata['description']} "
                
            if metadata.get('text_content'):
                # Use a portion of the text content if it's very long
                text_content = metadata['text_content']
                if len(text_content) > 10000:  # Limit to 10,000 characters
                    text_content = text_content[:10000]
                combined_text += text_content
            
            if not combined_text:
                return {
                    "page_type": "unknown",
                    "categories": [],
                    "topics": [],
                    "error": "Insufficient content for classification"
                }
            
            # Preprocess the text
            processed_text = self.preprocess_text(combined_text)
            
            # Determine page type based on URL, structure and metadata
            page_type = self._determine_page_type(metadata)
            
            # Determine categories
            categories = self._classify_categories(processed_text)
            
            # Extract topics
            topics = self._extract_topics(processed_text)
            
            return {
                "page_type": page_type,
                "categories": categories,
                "topics": topics
            }
            
        except Exception as e:
            logger.error(f"Error classifying content: {e}")
            return {
                "error": str(e),
                "page_type": "unknown",
                "categories": [],
                "topics": []
            }
    
    def _determine_page_type(self, metadata):
        """Determine the page type based on URL and structure."""
        url = metadata.get('url', '').lower()
        links = metadata.get('links', [])
        headings = metadata.get('headings', {})
        
        # Check for product pages
        if any(pattern in url for pattern in ['/product/', '/p/', '/item/']):
            return 'product'
            
        # Check for blog posts
        if any(pattern in url for pattern in ['/blog/', '/post/', '/article/']):
            return 'article'
            
        # Check for category pages
        if any(pattern in url for pattern in ['/category/', '/collection/', '/department/']):
            return 'category'
            
        # Check for homepage
        parsed_url = metadata.get('url', '')
        if parsed_url.endswith('/') and len(parsed_url.strip('/').split('/')) <= 1:
            return 'homepage'
            
        # Check if it's an article based on having many headings
        h1_count = len(headings.get('h1', []))
        h2_count = len(headings.get('h2', []))
        
        if h1_count == 1 and h2_count > 2:
            return 'article'
            
        # Default to generic page
        return 'generic'
    
    def _classify_categories(self, processed_text):
        """Classify the content into predefined categories."""
        token_set = set(processed_text.split())
        categories = []
        
        for category, keywords in self.categories.items():
            # Count how many keywords for this category appear in the text
            matches = sum(1 for keyword in keywords if keyword in token_set)
            if matches >= 2:  # Require at least 2 keyword matches
                categories.append({
                    "name": category,
                    "confidence": min(1.0, matches / len(keywords))  # Simple confidence score
                })
                
        # Sort by confidence
        categories.sort(key=lambda x: x['confidence'], reverse=True)
        
        return categories
    
    def _extract_topics(self, processed_text):
        """Extract main topics from the processed text."""
        if not processed_text:
            return []
            
        # Simple keyword extraction using word frequency
        words = processed_text.split()
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Get the top 10 most common words with length > 3
        topics = [word for word, count in word_counts.most_common(20) if len(word) > 3]
        
        # Keep only the top 10 topics
        topics = topics[:10]
        
        return topics

# For testing
if __name__ == "__main__":
    from crawler import WebCrawler
    from metadata_extractor import MetadataExtractor
    
    crawler = WebCrawler()
    extractor = MetadataExtractor()
    classifier = ContentClassifier()
    
    url = "https://www.example.com"
    result = crawler.crawl(url)
    
    if 'html_content' in result:
        metadata = extractor.extract_metadata(result['html_content'], url)
        classification = classifier.classify_page(metadata)
        
        print(f"Page type: {classification.get('page_type')}")
        print(f"Categories: {classification.get('categories')}")
        print(f"Topics: {classification.get('topics')}")