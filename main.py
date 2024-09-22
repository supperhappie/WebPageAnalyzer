from flask import Flask, render_template, request, jsonify
from web_scraper import get_website_text_content
from chat_request import send_openai_request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/crawl", methods=["POST"])
def crawl():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Crawl the website
        content = get_website_text_content(url)

        # Generate description using 4o-mini model
        prompt = f"Provide a brief description of the following website content:\n\n{content[:1000]}..."
        description = send_openai_request(prompt)

        return jsonify({"description": description})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
