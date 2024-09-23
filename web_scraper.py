import hashlib
from newspaper import Article
from typing import Dict, Tuple

# In-memory cache for checksums
checksum_cache: Dict[str, str] = {}

import sqlite3
from typing import Tuple

def get_website_text_content(url: str) -> Tuple[str, bool]:
    """
    This function takes a URL and returns the main text content of the website and a boolean indicating whether the content has changed.
    """
    print(f"Debug: Starting to process URL - {url}")

    # Connect to the database
    conn = sqlite3.connect('update_checker.db')
    cursor = conn.cursor()
    print("Debug: Database connection completed")

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS website_snapshots
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       url TEXT UNIQUE,
                       content_checksum TEXT,
                       content_description TEXT,
                       content_keywords TEXT)''')
    print("Debug: 테이블 생성 확인됨")

    # URL이 이전에 크롤링되었는지 확인
    cursor.execute("SELECT id, content_checksum FROM website_snapshots WHERE url = ?", (url,))
    result = cursor.fetchone()
    url_id, old_checksum = result if result else (None, None)
    print(f"Debug: URL ID - {url_id}")
    print(f"Debug: 이전 체크섬 - {old_checksum}")

    # Download and parse the article
    article = Article(url)
    article.download()
    article.parse()
    print("Debug: Article download and parsing completed")
    
    # Extract main content
    content = article.text
    print(f"Debug: Extracted content({len(content)}) : {content}")

    # Generate checksum for new content
    new_checksum = hashlib.md5(content.encode()).hexdigest()
    print(f"Debug: New checksum - {new_checksum}")
    # Update checksum in database
    if url_id:
        if old_checksum != new_checksum:
            cursor.execute("UPDATE website_snapshots SET content_checksum = ? WHERE id = ?", (new_checksum, url_id))
            print("Debug: Checksum has been updated")
        else:
            print("Debug: No changes in content")
    else:
        cursor.execute("INSERT INTO website_snapshots (url, content_checksum) VALUES (?, ?)", (url, new_checksum))
        url_id = cursor.lastrowid
        print("Debug: New checksum has been inserted")

    conn.commit()
    conn.close()
    print("Debug: Database connection closed")

    # Check if content has changed
    content_changed = old_checksum != new_checksum
    print(f"Debug: Content changed - {content_changed}")

    return url_id, content, content_changed