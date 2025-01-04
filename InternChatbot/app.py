from flask import Flask, request, jsonify, redirect, send_file, session
from flask_cors import CORS  # Add this import
import anthropic
from datetime import datetime
import os
from functools import wraps
from template import HTML_TEMPLATE

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)  # Enable CORS properly

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    current_hour = datetime.now().hour
    greeting = (
        "Good morning" if 5 <= current_hour < 12
        else "Good afternoon" if 12 <= current_hour < 18
        else "Having a late night?"
    )
    modified_template = HTML_TEMPLATE.replace('Having a late night?', greeting)
    return modified_template

@app.route('/login', methods=['GET'])
def login_page():
    return send_file('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    try:
        return send_file('signup.html')
    except FileNotFoundError:
        return jsonify({"error": "Signup page not available"}), 404

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Add your authentication logic here
        # For demo purposes, accept any valid email/password
        session['user_email'] = email
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {"email": email}
        })

    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        # Add your user creation logic here
        # For demo purposes, accept any valid email/password
        session['user_email'] = email
        return jsonify({
            "status": "success",
            "message": "Signup successful",
            "user": {"email": email}
        })

    except Exception as e:
        app.logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"})

@app.route('/chat', methods=['POST', 'OPTIONS'])
@login_required
def chat():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Handle different content types
        if request.content_type and 'multipart/form-data' in request.content_type:
            message = request.form.get('message', '')
            files = []
            
            # Handle multiple files
            if 'files[]' in request.files:
                uploaded_files = request.files.getlist('files[]')
                for file in uploaded_files:
                    if file:
                        content = file.read().decode('utf-8')
                        files.append({
                            'name': file.filename,
                            'content': content
                        })
        else:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            message = data.get('message', '')
            files = []

        if not message:
            return jsonify({"error": "Message content required"}), 400

        # Construct prompt with files if present
        content = message
        if files:
            files_content = "\n\n".join([
                f"File: {f['name']}\nContent:\n{f['content']}"
                for f in files
            ])
            content = f"{files_content}\n\nUser message: {message}"

        # Get chat response
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

        return jsonify({
            "status": "success",
            "response": response.content[0].text
        })

    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)