import os
from openai import OpenAI
import sqlite3
from typing import Tuple
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it and restart the application.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def send_openai_request_description(url_id: int, content: str, content_changed: bool) -> str:
    print(f"Debug: Starting send_openai_request_description function. url_id: {url_id}, content_changed: {content_changed}")
    prompt = f"Provide a brief description of the following website content:\n\n{content[:1000]}..."   # need custom : content
    print(f"Debug: Prompt to be sent to OpenAI - {prompt}")
    
    # Connect to the database
    conn = sqlite3.connect('update_checker.db')
    cursor = conn.cursor()
    print("Debug: Database connection completed")
    
    if not content_changed:
        print("Debug: Content has not changed. Attempting to retrieve existing description")
        # If content_changed is False, return the existing description
        cursor.execute("SELECT content_description FROM website_snapshots WHERE id = ?", (url_id,))
        result = cursor.fetchone()
        if result:
            print(f"Debug: Existing description found. Description: {result[0][:50]}...")
            conn.close()
            print("Debug: Database connection closed")
            return result[0]
        print("Debug: Existing description not found")
    
    try:
        print("Debug: Starting OpenAI API call")
        # Call OpenAI API
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=100 # need custom : max_tokens
        )
        description = completion.choices[0].message.content
        print(f"Debug: Received OpenAI response. Response description: {description[:50]}...")
        if not description:
            raise ValueError("OpenAI returned an empty response.")
        
        print("Debug: Starting to update new description in database")
        # Update new description in database
        cursor.execute("UPDATE website_snapshots SET content_description = ? WHERE id = ?", (description, url_id))
        conn.commit()
        print("Debug: Database update completed")
        
        return description
    except Exception as e:
        print(f"Debug: Error occurred - {str(e)}")
        raise Exception(f"Error in OpenAI request: {str(e)}")
    finally:
        conn.close()
        print("Debug: Database connection closed")
def send_openai_request_keywords(url_id: int, content: str, content_changed: bool) -> str:
    print(f"Debug: Starting send_openai_request_keywords function. url_id: {url_id}, content_changed: {content_changed}")
    prompt = f"Provide a list of keywords related to the following website content:\n\n{content[:1000]}..."   # need custom : content
    print(f"Debug: Prompt to be sent to OpenAI - {prompt}")
    
    # Connect to the database
    conn = sqlite3.connect('update_checker.db')
    cursor = conn.cursor()
    print("Debug: Database connection completed")
    
    if not content_changed:
        print("Debug: Content has not changed. Attempting to retrieve existing keywords")
        # If content_changed is False, return the existing keywords
        cursor.execute("SELECT content_keywords FROM website_snapshots WHERE id = ?", (url_id,))
        result = cursor.fetchone()
        if result:
            print(f"Debug: Existing keywords found. Keywords: {result[0][:50]}...")
            conn.close()
            print("Debug: Database connection closed")
            return result[0]
        print("Debug: Existing keywords not found")
        
    try:
        print("Debug: Starting OpenAI API call")
        # Call OpenAI API
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=50 # need custom : max_tokens
        )
        keywords = completion.choices[0].message.content
        print(f"Debug: Received OpenAI response. Response keywords: {keywords[:50]}...")
        if not keywords:
            raise ValueError("OpenAI returned an empty response.")
        
        print("Debug: Starting to update new keywords in database")
        # Update new keywords in database
        cursor.execute("UPDATE website_snapshots SET content_keywords = ? WHERE id = ?", (keywords, url_id))
        conn.commit()
        print("Debug: Database update completed")
        
        return keywords
    except Exception as e:
        print(f"Debug: Error occurred - {str(e)}")
        raise Exception(f"Error in OpenAI request: {str(e)}")
    finally:
        conn.close()
        print("Debug: Database connection closed")