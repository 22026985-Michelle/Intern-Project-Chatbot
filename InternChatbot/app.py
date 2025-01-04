from flask import Flask, request, jsonify
import anthropic
import json
from datetime import datetime
import os

app = Flask(__name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = ""
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Define HTML template directly in the file to avoid import issues
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Intern Assistant Chat</title>
</head>
<body>
    <h1>Welcome to Intern Assistant</h1>
    <div id="chat-container">
        <!-- Chat messages will appear here -->
    </div>
    <input type="text" id="message-input" placeholder="Type your message...">
    <button onclick="sendMessage()">Send</button>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the main chat interface"""
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Having a late night?"
    modified_template = HTML_TEMPLATE.replace('Welcome to', greeting + ' - Welcome to')
    return modified_template

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)