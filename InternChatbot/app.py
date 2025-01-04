from flask import Flask, request, jsonify
import anthropic
import json
from datetime import datetime
import os
from template import HTML_TEMPLATE

app = Flask(__name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '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')
if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY not set in environment variables")

try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except Exception as e:
    print(f"Error initializing Anthropic client: {str(e)}")
    client = None

@app.route('/')
def home():
    """Serve the main chat interface"""
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Having a late night?"
    modified_template = HTML_TEMPLATE.replace('Having a late night?', greeting)
    return modified_template

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        if not client:
            return jsonify({"error": "Anthropic client not initialized"}), 500

        if request.content_type and 'multipart/form-data' in request.content_type:
            message = request.form.get('message', '')
            file_content = None
            
            if 'file' in request.files:
                file = request.files['file']
                if file:
                    file_content = file.read().decode('utf-8')

            content = message
            if file_content:
                content = f"File content:\n{file_content}\n\nUser message:\n{message}"
        else:
            data = request.get_json()
            content = data.get('message', '')

        if not content:
            return jsonify({"error": "Message content missing"}), 400

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system="You are the Intern Assistant Chatbot, a helpful AI designed to assist interns and junior employees with their tasks. Be friendly and professional.",
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        return jsonify({"response": response.content[0].text})

    except Exception as e:
        print(f"Error handling chat request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.after_request
def after_request(response):
    """Add CORS headers"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)