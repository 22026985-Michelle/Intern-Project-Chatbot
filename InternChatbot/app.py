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

        app.logger.info(f"Login attempt for email: {email}")

        # Query the database to get the hashed password
        query = "SELECT user_id, password FROM users WHERE email = %s"
        result = execute_query(query, (email,))
        
        app.logger.info(f"Database query result: {result}")
        
        if result:
            stored_hashed_password = result[0]['password']
            if check_password_hash(stored_hashed_password, password):
                session['user_email'] = email
                session['user_id'] = result[0]['user_id']  # Store user_id in session
                app.logger.info(f"Login successful for {email}. Session data: {session}")
                return jsonify({"status": "success", "message": "Login successful"})
            else:
                app.logger.warning(f"Invalid password for {email}")
                return jsonify({"error": "Invalid credentials"}), 401
        else:
            app.logger.warning(f"No user found for email: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        app.logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
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

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat requests"""
    try:
        if not client:
            return jsonify({"error": "Anthropic client not initialized"}), 500

        # Get user ID from email in session
        user_email = session.get('user_email')
        if not user_email:
            app.logger.error("No user_email found in session")
            return jsonify({"error": "User not authenticated"}), 401
            
        app.logger.info(f"Looking up user with email: {user_email}")
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            app.logger.error(f"No user found for email: {user_email}")
            return jsonify({"error": "User not found"}), 404
        
        user_id = user_result[0]['id']
        app.logger.info(f"Found user_id: {user_id}")

        # Get or create chat session
        chat_query = "SELECT chat_id FROM chats WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1"
        chat_result = execute_query(chat_query, (user_id,))
        
        if not chat_result:
            app.logger.info(f"Creating new chat for user_id: {user_id}")
            chat_id = create_new_chat(user_id)
            if not chat_id:
                app.logger.error("Failed to create new chat")
                return jsonify({"error": "Failed to create chat session"}), 500
        else:
            chat_id = chat_result[0]['chat_id']
            
        # Get message content
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

        # Store user message
        app.logger.info(f"Adding user message to chat_id: {chat_id}")
        add_message(chat_id, content, is_user=True)

        # Get bot response
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

        bot_response = response.content[0].text
        
        # Store bot response
        app.logger.info(f"Adding bot response to chat_id: {chat_id}")
        add_message(chat_id, bot_response, is_user=False)

        # Cleanup old chats
        cleanup_old_chats(user_id)

        return jsonify({"response": bot_response})

    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
    
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
    """Log session data after each request"""
    app.logger.info(f"Current session data: {session}")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

@app.route('/api/create-chat', methods=['POST'])
@login_required
def create_chat():
    try:
        user_email = session.get('user_email')
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            return jsonify({"error": "User not found"}), 404
            
        user_id = user_result[0]['user_id']
        
        # Create new chat
        chat_id = create_new_chat(user_id)
        
        if not chat_id:
            return jsonify({"error": "Failed to create chat"}), 500
            
        return jsonify({"status": "success", "chat_id": chat_id})
        
    except Exception as e:
        app.logger.error(f"Error creating chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
@login_required
def get_chat_history():
    try:
        user_email = session.get('user_email')
        app.logger.info(f"Getting chat history for user: {user_email}")
        
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            app.logger.error(f"No user found for email: {user_email}")
            return jsonify({"error": "User not found"}), 404
            
        user_id = user_result[0]['user_id']
        app.logger.info(f"Found user_id: {user_id}")
        
        # Get recent chats (limit to 5)
        chats = get_recent_chats(user_id, limit=5)
        
        # Return empty array if no chats found
        return jsonify({"chats": chats or []})
        
    except Exception as e:
        app.logger.error(f"Error getting chat history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/<int:chat_id>/messages', methods=['GET'])
@login_required
def get_chat_messages(chat_id):
    try:
        # Verify the chat belongs to the current user
        user_email = session.get('user_email')
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            return jsonify({"error": "User not found"}), 404
            
        user_id = user_result[0]['user_id']
        
        # Check chat ownership
        chat_query = "SELECT user_id FROM chats WHERE chat_id = %s"
        chat_result = execute_query(chat_query, (chat_id,))
        
        if not chat_result or chat_result[0]['user_id'] != user_id:
            return jsonify({"error": "Chat not found"}), 404
        
        messages = get_chat_messages(chat_id)
        return jsonify({"messages": messages})
        
    except Exception as e:
        app.logger.error(f"Error getting chat messages: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/generate-title', methods=['POST'])
@login_required
def generate_chat_title():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        # Use Claude to generate a concise title
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            temperature=0,
            system="Generate a short, concise title (max 6 words) for a chat based on the first message.",
            messages=[{
                "role": "user",
                "content": message
            }]
        )
        
        title = response.content[0].text.strip()
        return jsonify({"title": title})
        
    except Exception as e:
        app.logger.error(f"Error generating title: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/<int:chat_id>/title', methods=['PUT'])
@login_required
def update_chat_title(chat_id):
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({"error": "Title is required"}), 400
            
        # Update title in database
        query = "UPDATE chats SET title = %s WHERE chat_id = %s"
        execute_query(query, (title, chat_id))
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"Error updating chat title: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update your get_recent_chats function to include titles
def get_recent_chats(user_id, limit=5):
    query = """
    SELECT c.chat_id, 
           c.title,
           m.content as last_message,
           c.created_at,
           c.updated_at,
           c.is_starred
    FROM chats c
    LEFT JOIN (
        SELECT chat_id, content, created_at,
               ROW_NUMBER() OVER (PARTITION BY chat_id ORDER BY created_at DESC) as rn
        FROM messages
    ) m ON c.chat_id = m.chat_id AND m.rn = 1
    WHERE c.user_id = %s
    ORDER BY c.is_starred DESC, c.updated_at DESC
    LIMIT %s
    """
    return execute_query(query, (user_id, limit))

@app.route('/api/chat/<int:chat_id>/star', methods=['PUT'])
@login_required
def toggle_star_chat(chat_id):
    try:
        data = request.get_json()
        is_starred = data.get('is_starred', False)
        
        # Update star status in database
        query = "UPDATE chats SET is_starred = %s WHERE chat_id = %s"
        execute_query(query, (is_starred, chat_id))
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"Error starring chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    try:
        # Delete chat and its messages
        delete_messages_query = "DELETE FROM messages WHERE chat_id = %s"
        execute_query(delete_messages_query, (chat_id,))
        
        delete_chat_query = "DELETE FROM chats WHERE chat_id = %s"
        execute_query(delete_chat_query, (chat_id,))
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"Error deleting chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chat/<int:chat_id>/section', methods=['PUT'])
@login_required
def update_chat_section(chat_id):
    try:
        data = request.get_json()
        section = data.get('section')
        
        if not section:
            return jsonify({"error": "Section is required"}), 400
            
        query = "UPDATE chats SET section = %s WHERE chat_id = %s"
        execute_query(query, (section, chat_id))
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"Error updating chat section: {str(e)}")
        return jsonify({"error": str(e)}), 500