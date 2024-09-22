import hashlib
from newspaper import Article
from typing import Dict, Tuple

# In-memory cache for checksums
checksum_cache: Dict[str, str] = {}

def get_website_text_content(url: str) -> Tuple[str, bool]:
    """
    This function takes a URL and returns the main text content of the website
    along with a boolean indicating whether the content has changed.
    """
    # Create a checksum of the URL
    url_checksum = hashlib.md5(url.encode()).hexdigest()

    # Check if the URL has been crawled before
    if url_checksum in checksum_cache:
        old_checksum = checksum_cache[url_checksum]
    else:
        old_checksum = None

    # Download and parse the article
    article = Article(url)
    article.download()
    article.parse()

    # Extract the main content
    content = article.text

    # Create a checksum of the new content
    new_checksum = hashlib.md5(content.encode()).hexdigest()

    # Update the checksum cache
    checksum_cache[url_checksum] = new_checksum

    # Check if the content has changed
    content_changed = old_checksum != new_checksum

    return content, content_changed

