import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it and restart the application.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def send_openai_request(prompt: str) -> str:
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=100
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response.")
        return content
    except Exception as e:
        raise Exception(f"Error in OpenAI request: {str(e)}")
