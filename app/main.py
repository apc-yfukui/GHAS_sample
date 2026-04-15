import os
import requests
from flask import Flask, request, render_template_string, render_template

app = Flask(__name__)

# [SECRET SCANNING DEMO]
# Dummy API Key to trigger GHAS Secret Scanning
DUMMY_OPENAI_API_KEY = "sk-antigravity-1234567890abcdef1234567890abcdef"

def mock_llm_call(prompt):
    """
    Simulates an LLM call. 
    In a real scenario, this would send the prompt to an API.
    """
    return f"AI Response to: {prompt[:50]}..."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    # [PROMPT INJECTION (LLM01) DEMO]
    # Vulnerability: Directly concatenating user input into the prompt.
    user_input = request.form.get("text", "")
    system_prompt = "Summarize the following text: "
    full_prompt = system_prompt + user_input  # TAINTED DATA
    
    response = mock_llm_call(full_prompt)
    return {"summary": response}

@app.route("/fetch", methods=["POST"])
def fetch_url():
    # [SSRF (A10:2021) DEMO]
    # Vulnerability: Fetching a user-provided URL without validation.
    target_url = request.form.get("url", "")
    try:
        # CodeQL should detect this as SSRF
        resp = requests.get(target_url, timeout=5)
        return {"content": resp.text[:200]}
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/preview", methods=["POST"])
def preview():
    # [XSS (A03:2021) DEMO]
    # Vulnerability: Returning unsanitized content to be rendered via innerHTML.
    content = request.form.get("content", "")
    # In index.html, this will be injected via JS innerHTML
    return {"html": content}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
