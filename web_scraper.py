from typing import Dict, Tuple, List
from newspaper import Article
import hashlib
import sqlite3
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from chat_request import send_openai_request

def get_langchain_sitemap_urls() -> List[str]:
    # In-memory cache for checksums
    checksum_cache: Dict[str, str] = {}

    # Fetch the XML sitemap
    response = requests.get("https://python.langchain.com/sitemap.xml")

    # Parse the XML content
    root = ET.fromstring(response.content)

    # Initialize a list to store URLs
    urls = []

    # Iterate over all <loc> tags in the XML and extract URLs
    for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        urls.append(url.text)

    return urls

def get_langchain_api_reference_urls() -> List[str]:
    # URL of the page with the sidebar navigation items
    url_api_reference = "https://python.langchain.com/api_reference/"
    response = requests.get(url_api_reference)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'a' tags within the 'ul' elements with class 'nav bd-sidenav'
    links = soup.find_all('ul', class_='nav bd-sidenav')

    # Initialize a list to store the href values
    hrefs = []

    # Loop through each 'ul.nav.bd-sidenav' and extract all 'a' hrefs
    for ul in links:
        for a in ul.find_all('a', href=True):
            hrefs.append(a['href'])

    # Print the list of URLs
    return(hrefs)



def get_website_text_content(url: str) -> Tuple[int, str, bool]:
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

# test code 
# urls = get_langchain_sitemap_urls()
# print(urls)
# urls = get_langchain_api_reference_urls()
# print(urls)

def update_website_description_and_keywords():
    sitemap_urls = get_langchain_sitemap_urls()
    api_reference_urls = get_langchain_api_reference_urls()
    max_urls = len(sitemap_urls) + len(api_reference_urls)
    cnt = 0
    for url in sitemap_urls:
        url_id, content, content_changed = get_website_text_content(url)
        description, keywords = send_openai_request(url_id=url_id, content=content, content_changed=content_changed)
        cnt += 1
        print(f"[{cnt}/{max_urls}] \n\tdescription: {description[:100]}\n\tkeywords: {keywords[:100]}")

    for url in api_reference_urls:
        url_id, content, content_changed = get_website_text_content(url)
        description, keywords = send_openai_request(url_id=url_id, content=content, content_changed=content_changed)
        cnt += 1
        print(f"[{cnt}/{max_urls}] \n\tdescription: {description[:100]}\n\tkeywords: {keywords[:100]}")


update_website_description_and_keywords()