from flask import Flask, request, jsonify, redirect, send_file, session
import anthropic
from datetime import datetime
import os
from functools import wraps
from template import HTML_TEMPLATE
from database import get_db_connection, execute_query, create_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

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
    
    # First get the user's email from session
    user_email = session.get('user_email', '')
    
    # Get the first letter of the email for the avatar
    avatar_letter = user_email[0].upper() if user_email else 'U'
    
    # Replace all placeholders in the template
    modified_template = HTML_TEMPLATE.replace('Having a late night?', greeting)
    modified_template = modified_template.replace('{avatar_letter}', avatar_letter)
    modified_template = modified_template.replace('{email}', user_email)
    
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

        # Query the database to get the hashed password
        query = "SELECT password FROM users WHERE email = %s"
        result = execute_query(query, (email,))
        
        if result:
            stored_hashed_password = result[0]['password']
            if check_password_hash(stored_hashed_password, password):
                session['user_email'] = email
                return jsonify({"status": "success", "message": "Login successful"})
            else:
                return jsonify({"error": "Invalid credentials"}), 401
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(f"Error handling login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

def is_password_strong(password):
    """
    Validate password strength.
    Password should:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character (!@#$%^&* etc.)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, None

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        if not email or not password or not username:
            return jsonify({"error": "Email, password, and username are required"}), 400

        # Validate password strength
        is_strong, message = is_password_strong(password)
        if not is_strong:
            return jsonify({"error": message}), 400

        app.logger.info(f"Attempting to create user with email: {email}")

        # Pass username to create_user
        success, message = create_user(email, password, username)

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
    
@app.route('/api/get-profile')
@login_required
def get_profile():
    """Get user profile data"""
    try:
        email = session['user_email']
        query = "SELECT username, email FROM users WHERE email = %s"
        result = execute_query(query, (email,))
        
        if result:
            return jsonify({
                "name": result[0]['username'],
                "email": result[0]['email']
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        email = session['user_email']
        data = request.form
        
        updates = []
        params = []
        
        if data.get('name'):
            updates.append("username = %s")
            params.append(data['name'])
            
        if data.get('newPassword'):
            updates.append("password = %s")
            params.append(generate_password_hash(data['newPassword']))
            
        if not updates:
            return jsonify({"error": "No updates provided"}), 400
            
        params.append(email)
        query = f"UPDATE users SET {', '.join(updates)} WHERE email = %s"
        
        execute_query(query, tuple(params))
        
        return jsonify({"status": "success", "message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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