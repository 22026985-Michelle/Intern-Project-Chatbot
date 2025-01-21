from flask import Flask, request, jsonify, redirect, send_file, session, make_response
import anthropic
from datetime import datetime
import os
import json
from functools import wraps
from template import HTML_TEMPLATE
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dynamic_formatter import DynamicFormatter
import logging
logger = logging.getLogger(__name__)
from database import (
    get_db_connection, 
    execute_query, 
    create_user, 
    create_new_chat, 
    get_recent_chats, 
    add_message, 
    cleanup_old_chats,
    FileHandler,
    handle_conversion_request,
    process_json_to_table
)
from io import StringIO
import csv

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = os.urandom(24)
formatter = DynamicFormatter()

UPLOAD_FOLDER = 'static/profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/export-table', methods=['POST'])
def export_table():
    """Handle table data export"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = list(data.keys())
        writer.writerow(headers)
        
        # Write values
        values = list(data.values())
        writer.writerow(values)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=table_data.csv'
        response.headers['Content-type'] = 'text/csv'
        
        return response

    except Exception as e:
        app.logger.error(f"Error exporting table: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

# app.py changes - Update the chat route:

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        if not client:
            return jsonify({"error": "Anthropic client not initialized"}), 500

        data = request.get_json()
        message = data.get('message', '')
        chat_id = data.get('chat_id')

        # Create new chat if no chat_id provided
        if not chat_id:
            user_email = session.get('user_email')
            user_query = "SELECT user_id FROM users WHERE email = %s"
            user_result = execute_query(user_query, (user_email,))
            if not user_result:
                return jsonify({"error": "User  not found"}), 404
            
            user_id = user_result[0]['user_id']
            chat_id = create_new_chat(user_id)
            if not chat_id:
                return jsonify({"error": "Failed to create chat"}), 500

            # Set chat title based on the first message
            title = message[:50]  # Limit title length to 50 characters
            update_chat_title(chat_id, title)

        # Store user message
        add_message(chat_id, message, is_user=True)

        # Regular chat processing
        message_history = []
        messages_query = "SELECT content, is_user FROM messages WHERE chat_id = %s ORDER BY created_at ASC"
        previous_messages = execute_query(messages_query, (chat_id,))
        
        for msg in previous_messages:
            role = "user" if msg['is_user'] else "assistant"
            message_history.append({"role": role, "content": msg['content']})

        message_history.append({"role": "user", "content": message})
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            messages=message_history
        )
        
        bot_response = response.content[0].text

        # Format the bot response if it's JSON
        if bot_response.startswith('{') or bot_response.startswith('['):
            try:
                parsed_json = json.loads(bot_response)  # Parse the JSON
                formatted_json = json.dumps(parsed_json, indent=2)  # Format with indentation
                bot_response = formatted_json  # Update the bot response
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from bot response.")

        # Store bot response
        add_message(chat_id, bot_response, is_user=False)
        
        return jsonify({
            "response": bot_response,
            "chat_id": chat_id
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/format-json', methods=['POST'])
@login_required
def format_json():
    try:
        data = request.get_json()
        json_data = data.get('json_data')

        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Use the DynamicFormatter to format the JSON
        formatted_json = formatter.format_json(json_data)

        return jsonify({
            "formatted_json": formatted_json
        })

    except Exception as e:
        logger.error(f"Error formatting JSON: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
def format_json_data(message):
    """Handle JSON formatting requests"""
    try:
        formatter = DynamicFormatter()
        # Extract JSON data from the subsequent messages
        # This is a placeholder - you'll need to implement the actual JSON extraction
        json_data = extract_json_from_message(message)
        if json_data:
            result = formatter.process_data(json_data)
            return result.get('json', 'Could not format JSON data')
        return "Please provide the JSON data you'd like to format."
    except Exception as e:
        logger.error(f"Error formatting JSON: {str(e)}")
        return f"Error formatting JSON: {str(e)}"
    

def process_regular_chat(message, chat_id):
    """Handle regular chat messages"""
    try:
        # Get previous messages for context
        messages_query = """
        SELECT content, is_user 
        FROM messages 
        WHERE chat_id = %s 
        ORDER BY created_at ASC
        """
        previous_messages = execute_query(messages_query, (chat_id,))
        
        message_history = []
        for msg in previous_messages:
            role = "user" if msg['is_user'] else "assistant"
            message_history.append({"role": role, "content": msg['content']})

        message_history.append({"role": "user", "content": message})

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            messages=message_history
        )
        return response.content[0].text.replace('```json', '').replace('```', '')
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise

def extract_json_from_message(message):
    """Extract JSON data from message"""
    try:
        # Look for JSON-like content in the message
        start_idx = message.find('{')
        end_idx = message.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = message[start_idx:end_idx + 1]
            return json_str
        return None
    except Exception:
        return None
    
@app.route('/api/get-profile')
@login_required
def get_profile():
    """Get user profile data"""
    try:
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Not authenticated"}), 401

        query = "SELECT username, email, profile_picture FROM users WHERE email = %s"
        result = execute_query(query, (email,))
        
        if result and result[0]:
            return jsonify({
                "name": result[0]['username'],
                "email": result[0]['email'],
                "profilePicture": result[0]['profile_picture']
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        app.logger.error(f"Error getting profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        email = session.get('user_email')
        if not email:
            return jsonify({"error": "Not authenticated"}), 401

        updates = []
        params = []
        
        # Handle name update
        if 'name' in request.form:
            updates.append("username = %s")
            params.append(request.form['name'])
        
        # Handle password update
        if request.form.get('newPassword'):
            updates.append("password = %s")
            params.append(generate_password_hash(request.form['newPassword']))
        
        # Handle profile picture upload
        if 'profilePicture' in request.files:
            file = request.files['profilePicture']
            if file and file.filename and allowed_file(file.filename):
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Create unique filename
                filename = secure_filename(f"{email}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save file
                file.save(filepath)
                
                # Update database with relative path
                updates.append("profile_picture = %s")
                params.append(f"/static/profile_pictures/{filename}")

        if not updates:
            return jsonify({"error": "No updates provided"}), 400
            
        params.append(email)
        query = f"UPDATE users SET {', '.join(updates)} WHERE email = %s"
        
        execute_query(query, tuple(params))
        
        return jsonify({"status": "success", "message": "Profile updated successfully"})
    except Exception as e:
        app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    """Log session data after each request"""
    app.logger.info(f"Current session data: {session}")
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')  
    return response

@app.route('/api/create-chat', methods=['POST'])
@login_required
def create_chat():
    try:
        user_email = session.get('user_email')
        if not user_email:
            app.logger.error("User email not found in session")
            return jsonify({"error": "User not authenticated"}), 401

        # Get user ID
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            app.logger.error(f"No user found for email: {user_email}")
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]['user_id']
        app.logger.info(f"Creating chat for user_id: {user_id}")

        # Create new chat
        chat_id = create_new_chat(user_id)
        if not chat_id:
            app.logger.error("Failed to create chat")
            return jsonify({"error": "Failed to create chat"}), 500

        app.logger.info(f"Successfully created chat with ID: {chat_id}")
        return jsonify({
            "status": "success",
            "chat_id": chat_id
        })

    except Exception as e:
        app.logger.error(f"Error creating chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

@app.route('/api/chat-history', methods=['GET'])
@login_required
def get_chat_history():
    try:
        user_email = session.get('user_email')
        if not user_email:
            app.logger.error("User email not found in session")
            return jsonify({"error": "User not authenticated"}), 401

        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        if not user_result:
            app.logger.error(f"No user found for email: {user_email}")
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]['user_id']
        app.logger.info(f"Fetching chat history for user_id: {user_id}")

        # Get chats with their latest messages and titles
        chats = get_recent_chats(user_id, 5)
        app.logger.info(f"Retrieved chats: {chats}")

        return jsonify({
            "status": "success",
            "chats": chats or []
        }), 200

    except Exception as e:
        app.logger.error(f"Error in get_chat_history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/<int:chat_id>/messages', methods=['GET'])
@login_required
def get_chat_messages(chat_id):
    try:
        user_email = session.get('user_email')
        user_query = "SELECT user_id FROM users WHERE email = %s"
        user_result = execute_query(user_query, (user_email,))
        
        if not user_result:
            return jsonify({"error": "User not found"}), 404
            
        user_id = user_result[0]['user_id']
        
        # Get messages directly
        messages_query = """
        SELECT message_id, chat_id, content, is_user, created_at
        FROM messages 
        WHERE chat_id = %s 
        ORDER BY created_at ASC
        """
        
        messages = execute_query(messages_query, (chat_id,))
        formatted_messages = []
        
        if messages:
            for msg in messages:
                formatted_messages.append({
                    'message_id': msg['message_id'],
                    'content': msg['content'],
                    'is_user': bool(msg['is_user']),
                    'created_at': msg['created_at'].strftime('%Y-%m-%d %H:%M:%S') if msg['created_at'] else None
                })
                
        return jsonify({
            'status': 'success',
            'messages': formatted_messages
        })

    except Exception as e:
        app.logger.error(f"Error getting chat messages: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
def generate_chat_title(message):
    try:
        # Use Claude to generate title
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            temperature=0,
            system="Generate a very concise chat title (2-4 words) based on the first message.",
            messages=[{"role": "user", "content": f"Create a brief title for: {message}"}]
        )
        title = response.content[0].text.strip()
        return title
    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        return "New Chat"

def update_chat_title(chat_id, title):
    """Update chat title"""
    try:
        update_query = "UPDATE chats SET title = %s WHERE chat_id = %s"
        execute_query(update_query, (title, chat_id))
        return True
    except Exception as e:
        logger.error(f"Error updating chat title: {str(e)}")
        return False
    
@app.route('/api/chat/<int:chat_id>/title', methods=['PUT'])
@login_required
def update_chat_title_endpoint(chat_id):
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({"error": "Title is required"}), 400
            
        # Update the chat title
        query = "UPDATE chats SET title = %s WHERE chat_id = %s"
        execute_query(query, (title, chat_id))
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        app.logger.error(f"Error updating chat title: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/chat/<int:chat_id>/title', methods=['OPTIONS'])
def chat_title_options(chat_id):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'PUT')
    return response

# Update your get_recent_chats function to include titles
def get_recent_chats(user_id, limit=5):
    query = """
    SELECT c.chat_id, 
           c.title,
           m.content as last_message,
           c.created_at,
           c.updated_at
    FROM chats c
    LEFT JOIN (
        SELECT chat_id, content, created_at,
               ROW_NUMBER() OVER (PARTITION BY chat_id ORDER BY created_at DESC) as rn
        FROM messages
    ) m ON c.chat_id = m.chat_id AND m.rn = 1
    WHERE c.user_id = %s
    ORDER BY c.updated_at DESC
    LIMIT %s
    """
    return execute_query(query, (user_id, limit))

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
    
@app.route('/api/move-chat-to-recents/<int:chat_id>', methods=['PUT'])
@login_required
def move_chat_to_recents(chat_id):
    """Move a chat to the 'Recents' section."""
    try:
        # Update the section of the chat to 'Recents'
        update_query = "UPDATE chats SET section = 'Recents' WHERE chat_id = %s"
        execute_query(update_query, (chat_id,))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/test-db')
def test_db():
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return jsonify({"status": "success", "message": "Database connection successful"})
    except Exception as e:
        app.logger.error(f"Database test failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route('/format', methods=['POST'])
def format_data():
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'No content provided'}), 400
            
        content = data['content']
        if not isinstance(content, (str, dict)):
            return jsonify({'error': 'Invalid content format'}), 400
            
        result = formatter.process_data(content)
        
        return jsonify({
            'status': 'success',
            'formatted_json': result['json'],
            'formatted_tabular': result['tabular']
        })
        
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/json-to-table', methods=['POST'])
@login_required
def json_to_table():
    try:
        data = request.get_json()
        json_data = data.get('json_data')
        
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Process the JSON data
        table_data = process_json_to_table(json_data)
        
        if not table_data:
            return jsonify({"error": "Failed to process JSON data"}), 500
            
        return jsonify({
            "status": "success",
            "data": table_data
        })
        
    except Exception as e:
        app.logger.error(f"Error converting JSON to table: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
