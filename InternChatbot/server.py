from flask import Flask, request, jsonify
import anthropic
import json
from datetime import datetime
from template import HTML_TEMPLATE
import os

app = Flask(__name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = "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"
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

@app.after_request
def after_request(response):
    """Add CORS and other necessary headers"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, ngrok-skip-browser-warning, User-Agent')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('ngrok-skip-browser-warning', 'true')
    response.headers.add('User-Agent', 'Mozilla/5.0')
    return response

@app.route('/')
def home():
    """Serve the main chat interface"""
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Having a late night?"
    modified_template = HTML_TEMPLATE.replace('Good afternoon', greeting)
    return modified_template

@app.route('/login')
def login():
    """Serve the login page"""
    try:
        with open('login.html', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Login page not found", 404

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload with message
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
            # Handle JSON request
            data = request.get_json()
            content = data.get('message', '')

        if not content:
            return jsonify({"error": "Message content missing"}), 400

        # Get response from Anthropic
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

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login API requests"""
    try:
        data = request.get_json()
        # Add your login logic here
        response_data = {"status": "success", "message": "Login successful"}
        return jsonify(response_data)
    except Exception as e:
        print(f"Error handling login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle signup API requests"""
    try:
        data = request.get_json()
        # Add your signup logic here
        response_data = {"status": "success", "message": "Signup successful"}
        return jsonify(response_data)
    except Exception as e:
        print(f"Error handling signup: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)