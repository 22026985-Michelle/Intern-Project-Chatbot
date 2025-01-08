from flask import Flask, request, jsonify, redirect, send_file, session
import anthropic
from datetime import datetime
import os
from functools import wraps
from template import HTML_TEMPLATE
from database import get_db_connection, execute_query, create_user

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except Exception as e:
    print(f"Error initializing Anthropic client: {str(e)}")
    client = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    """Serve the main chat interface"""
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Having a late night?"
    modified_template = HTML_TEMPLATE.replace('Having a late night?', greeting)
    return modified_template

@app.route('/login')
def login_page():
    """Serve the login page"""
    return send_file('login.html')

@app.route('/signup')
def signup_page():
    """Serve the signup page"""
    return send_file('signup.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login API requests"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Query the database
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        result = execute_query(query, (email, password))
        
        if result:
            session['user_email'] = email
            return jsonify({"status": "success", "message": "Login successful"})
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(f"Error handling login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')  # Add this line

        if not email or not password or not username:  # Modify this line
            return jsonify({"error": "Email, password, and username are required"}), 400

        app.logger.info(f"Attempting to create user with email: {email}")
        
        # Pass username to create_user
        success, message = create_user(email, password, username)  # Modify this line
        
        if success:
            session['user_email'] = email
            app.logger.info(f"Successfully created user: {email}")
            return jsonify({
                "status": "success",
                "message": "Signup successful"
            })
        else:
            app.logger.error(f"Failed to create user: {message}")
            return jsonify({
                "error": message
            }), 400

    except Exception as e:
        app.logger.error(f"Error in signup: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/Settings')
@login_required
def settings_page():
    """Serve the settings page"""
    return send_file('settings.html')

@app.route('/logout')
def logout():
    """Handle logout"""
    session.clear()
    return redirect('/login')

@app.route('/chat', methods=['POST'])
@login_required
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