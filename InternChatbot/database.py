import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import pandas as pd
import json
from flask import jsonify
from datetime import datetime
from typing import Union, Dict, List, Any
import re
from io import StringIO
from cryptography.fernet import Fernet

__all__ = [
    'get_db_connection',
    'execute_query',
    'create_user',
    'create_new_chat',
    'get_recent_chats',
    'add_message',
    'cleanup_old_chats',
    'handle_conversion_request'
]


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_message(message):
    """Encrypts the message using Fernet symmetric encryption."""
    return cipher.encrypt(message.encode())

def decrypt_message(encrypted_message):
    """Decrypts the encrypted message using Fernet symmetric encryption."""
    return cipher.decrypt(encrypted_message).decode()

def get_db_connection():
    """Get database connection with retry mechanism"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            config = {
                'host': '34.142.254.175',
                'user': 'root',
                'password': 'ILOVESUSHI123!',
                'database': 'internchatbot',
                'port': 3306,
                'connect_timeout': 30,
                'use_pure': True,
                'allow_local_infile': True,
                'auth_plugin': 'mysql_native_password',
                'pool_name': 'mypool',
                'pool_size': 5,
                'buffered': True
            }
            
            logger.info(f"Attempting to connect to MySQL (Attempt {retry_count + 1})")
            connection = mysql.connector.connect(**config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                logger.info(f"Successfully connected to MySQL. Server version: {db_info}")
                return connection
                
        except Error as e:
            logger.error(f"Error connecting to MySQL (Attempt {retry_count + 1}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)  # Wait 1 second before retrying
    
    logger.error("Failed to connect to database after maximum retries")
    return None

def execute_query(query, params=None):
    """Execute database query with proper error handling"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to connect to the database")
            return None

        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute(query, params)
        
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            if cursor.lastrowid:
                return cursor.lastrowid
            return cursor.rowcount

    except Error as e:
        logger.error(f"Database query error: {str(e)}")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def create_user(email, password, username):  # Add username parameter
    logger.info(f"Attempting to create user with email: {email}")
    
    # Check if email already exists
    check_query = "SELECT email FROM users WHERE email = %s"
    result = execute_query(check_query, (email,))
    
    if result:
        logger.info(f"User with email {email} already exists")
        return False, "Email already exists"
    
    # Hash and salt the password before storing
    hashed_password = generate_password_hash(password)
    
    # Insert new user
    insert_query = """
    INSERT INTO users (username, email, password, role, created_at) 
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        current_time = datetime.now()
        params = (username, email, hashed_password, 'user', current_time)  # Store hashed password
        rows_affected = execute_query(insert_query, params)
        
        if rows_affected:
            logger.info(f"Successfully created user with email {email}")
            return True, "User created successfully"
        logger.error(f"Failed to create user with email {email}")
        return False, "Failed to create user"
    except Error as e:
        logger.error(f"Error creating user: {str(e)}")
        return False, str(e)
    
def create_new_chat(user_id):
    """Create a new chat session for a user"""
    try:
        # Check and cleanup old chats if needed
        count_query = "SELECT COUNT(*) as chat_count FROM chats WHERE user_id = %s"
        result = execute_query(count_query, (user_id,))
        
        if result and result[0]['chat_count'] >= 5:
            cleanup_old_chats(user_id, keep_count=4)
        
        # Insert new chat with default title
        insert_query = """
        INSERT INTO chats (user_id, title, created_at, updated_at)
        VALUES (%s, %s, NOW(), NOW())
        """
        chat_id = execute_query(insert_query, (user_id, "New Chat"))
        
        return chat_id
        
    except Exception as e:
        logger.error(f"Error in create_new_chat: {str(e)}")
        return None

def add_message(chat_id, content, is_user=True):
    """Add a message to a chat session"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False

        cursor = connection.cursor(dictionary=True)
        encrypted_content = encrypt_message(content)
        
        # Add message
        message_query = """
        INSERT INTO messages (chat_id, content, is_user, created_at)
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(message_query, (chat_id, encrypted_content, is_user))
        
        # Update chat timestamp
        update_query = """
        UPDATE chats SET updated_at = NOW()
        WHERE chat_id = %s
        """
        cursor.execute(update_query, (chat_id,))
        
        connection.commit()
        return True

    except Error as e:
        logger.error(f"Error in add_message: {str(e)}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
def get_recent_chats(user_id, limit=5):
    """Get recent chats for a user"""
    query = """
    SELECT c.chat_id, 
           COALESCE(c.title, 'New Chat') as title,
           c.created_at,
           c.updated_at,
           (SELECT m.content 
            FROM messages m 
            WHERE m.chat_id = c.chat_id 
            ORDER BY m.created_at DESC 
            LIMIT 1) as last_message
    FROM chats c
    WHERE c.user_id = %s
    ORDER BY c.updated_at DESC
    LIMIT %s
    """
    try:
        result = execute_query(query, (user_id, limit))
        logger.info(f"Recent chats query result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in get_recent_chats: {str(e)}")
        return []

def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    query = """
    SELECT content, 
           is_user, 
           created_at
    FROM messages
    WHERE chat_id = %s
    ORDER BY created_at ASC
    """
    try:
        result = execute_query(query, (chat_id,))
        logger.info(f"Retrieved {len(result) if result else 0} messages for chat {chat_id}")
        
        if not result:
            return []
            
        # Ensure all fields are serializable
        for message in result:
            message['content'] = decrypt_message(message['content'])
            if 'created_at' in message and message['created_at']:
                message['created_at'] = message['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return result
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        return []

def cleanup_old_chats(user_id, keep_count=4):
    """Delete old chats, keeping only the specified number of most recent ones"""
    connection = None
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to connect to database")
            return

        cursor = connection.cursor(dictionary=True)
        
        # First get the IDs of chats to keep
        keep_query = """
        SELECT chat_id FROM chats 
        WHERE user_id = %s 
        ORDER BY updated_at DESC 
        LIMIT %s
        """
        cursor.execute(keep_query, (user_id, keep_count))
        keep_chats = cursor.fetchall()
        keep_ids = [chat['chat_id'] for chat in keep_chats]
        
        if keep_ids:
            # Delete all chats except the ones we want to keep
            delete_query = """
            DELETE FROM chats 
            WHERE user_id = %s 
            AND chat_id NOT IN ({})
            """.format(','.join(['%s'] * len(keep_ids)))
            
            cursor.execute(delete_query, (user_id, *keep_ids))
        else:
            # If no chats to keep, delete all chats for the user
            delete_query = "DELETE FROM chats WHERE user_id = %s"
            cursor.execute(delete_query, (user_id,))
        
        connection.commit()
        
    except Error as e:
        logger.error(f"Error in cleanup_old_chats: {str(e)}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def get_user_by_email(email):
    """Get user details by email"""
    logger.info(f"Looking up user with email: {email}")
    query = "SELECT user_id, username, email, role FROM users WHERE email = %s"
    result = execute_query(query, (email,))
    logger.info(f"User lookup result: {result}")
    return result[0] if result else None

def update_chat_title(chat_id, title):
    """Update chat title"""
    try:
        update_query = "UPDATE chats SET title = %s WHERE chat_id = %s"
        execute_query(update_query, (title, chat_id))
        return True
    except Exception as e:
        logger.error(f"Error updating chat title: {str(e)}")
        return False
    
def update_chat_section(chat_id, section):
    """Update chat section in database"""
    try:
        query = """
        UPDATE chats 
        SET section = %s, updated_at = NOW() 
        WHERE chat_id = %s
        """
        return execute_query(query, (section, chat_id))
    except Exception as e:
        logger.error(f"Error updating chat section: {str(e)}")
        return None
    
def convert_json_to_table(json_data):
    """Convert JSON to table format"""
    try:
        # Flatten the JSON structure
        flattened_data = {}
        for section, content in json_data.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flattened_data[f"{section}_{key}_{subkey}"] = str(subvalue)
                    else:
                        flattened_data[f"{section}_{key}"] = str(value) if value != "" else "-"
            else:
                flattened_data[section] = str(content) if content != "" else "-"

        # Create DataFrame
        df = pd.DataFrame([flattened_data])
        
        # Generate formatted table
        headers = list(df.columns)
        
        # Create table string
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["---" for _ in headers]) + "|\n"
        table += "| " + " | ".join([str(v) if v != "" else "-" for v in df.iloc[0]]) + " |"
        
        return table
        
    except Exception as e:
        logger.error(f"Error converting to table: {str(e)}")
        return None
    
def convert_tabular_to_json(text):
    """Convert tabular data to JSON format"""
    try:
        # Split into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Get headers
        if '|' in lines[0]:
            # Handle markdown table format
            headers = [h.strip() for h in lines[0].strip('|').split('|') if h.strip()]
            data_lines = lines[2:] if len(lines) > 2 else []  # Skip separator line
            separator = '|'
        else:
            # Handle space/tab separated
            headers = lines[0].split()
            data_lines = lines[1:]
            separator = None
            
        # Parse data into structured format
        structured_data = {}
        if data_lines:
            if separator:
                values = [v.strip() for v in data_lines[0].strip('|').split('|') if v.strip()]
            else:
                values = data_lines[0].split()
                
            # Group by section
            current_section = None
            for header, value in zip(headers, values):
                if '_' in header:
                    section, field = header.split('_', 1)
                    if section != current_section:
                        current_section = section
                        if current_section not in structured_data:
                            structured_data[current_section] = {}
                    structured_data[current_section][field] = value
                else:
                    structured_data[header] = value
        
        # Format JSON with proper indentation
        return json.dumps(structured_data, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error converting to JSON: {str(e)}")
        return None

def handle_conversion_request(message, previous_messages):
    """Handle data conversion with automatic format detection"""
    if not previous_messages:
        # Step 1: Initial request
        return "I don't see any data provided. Could you please share the data you'd like to convert?"
    
    previous_request = previous_messages[-1]
    if "Could you please share the data" in previous_request['content']:
        # Step 2: Data provided, detect format and convert
        data = message.strip()
        if len(data.split('\n')) <= 1:
            return "Please provide the actual data you want to convert."
            
        # Detect format and convert automatically
        try:
            # Try parsing as JSON first
            json.loads(data)
            # If successful, it's JSON - convert to table
            table = convert_json_to_table(json.loads(data))
            return f"I see you've provided JSON data. Here's your converted data in tabular format:\n\n{table}"
        except json.JSONDecodeError:
            # Not JSON, assume it's tabular - convert to JSON
            result = convert_tabular_to_json(data)
            return f"I see you've provided tabular data. Here's your converted data in JSON format:\n\n{result}"
    
    # Step 3: Process previous data
    data = previous_messages[-2]['content']
    try:
        json.loads(data)
        table = convert_json_to_table(json.loads(data))
        return f"Here's your data in tabular format:\n\n{table}"
    except json.JSONDecodeError:
        result = convert_tabular_to_json(data)
        return f"Here's your data in JSON format:\n\n{result}"
    
def detect_format(text):
    """Enhanced format detection"""
    text = text.strip()
    # Check for JSON format
    if (text.startswith('{') and text.endswith('}')) or \
       (text.startswith('[') and text.endswith(']')):
        try:
            json.loads(text)
            return 'json'
        except json.JSONDecodeError:
            pass
            
    # Look for tabular indicators
    lines = text.split('\n')
    if len(lines) > 1:
        # Check for consistent delimiters and header row
        first_line = lines[0].strip()
        if '|' in first_line or '\t' in first_line or ',' in first_line:
            return 'tabular'
        # Check if it looks like space-separated column headers
        if len(first_line.split()) > 1 and \
           all(not c.isdigit() for c in first_line):
            return 'tabular'
            
    return 'tabular'

def convert_format(text, source_format):
    """Enhanced format conversion with proper formatting"""
    try:
        if source_format == 'json':
            # Convert JSON to tabular using pandas
            data = json.loads(text)
            # Flatten nested JSON structure
            flattened_data = []
            
            def flatten_dict(d, parent_key=''):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}_{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key).items())
                    elif isinstance(v, list):
                        items.append((new_key, ','.join(map(str, v))))
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            if isinstance(data, dict):
                flattened_data.append(flatten_dict(data))
            else:
                for item in data:
                    flattened_data.append(flatten_dict(item))
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(flattened_data)
            
            # Format DataFrame as markdown table
            return df.to_markdown(index=False)

        else:
            # Convert tabular to JSON with proper formatting
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Parse headers and data
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            data = {}
            values = [v.strip() for v in lines[-1].split('|') if v.strip()]
            
            # Build structured data
            current_section = None
            for header, value in zip(headers, values):
                if '_' in header:
                    section, field = header.split('_', 1)
                    if section != current_section:
                        current_section = section
                        if current_section not in data:
                            data[current_section] = {}
                    data[current_section][field] = value
                else:
                    data[header] = value
            
            # Format JSON with proper indentation
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Add newlines for better readability
            return formatted_json

    except Exception as e:
        logger.error(f"Error converting format: {str(e)}")
        return f"Error converting format: {str(e)}"

def parse_text_data(text):
    """Parse copy-pasted text data into structured format"""
    try:
        # Split the text into lines and process
        lines = text.strip().split('\n')
        # Basic validation
        if len(lines) < 2:  # At least headers and one data row
            return None
            
        # Convert to proper structure
        data = {}
        # Add processing logic here based on your data structure
        return data
    except Exception as e:
        logger.error(f"Error parsing text data: {str(e)}")
        return None

class FileHandler:
    def __init__(self):
        self.supported_formats = {
            'excel': ['.xlsx', '.xls'],
            'csv': ['.csv'],
            'json': ['.json', '.txt']
        }
        
    def process_data(self, data, reference_format=None):
        """Process data according to reference format"""
        try:
            if reference_format:
                formatted_data = self._apply_reference_format(data, reference_format)
                return json.dumps(formatted_data, indent=2)
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

    def process_file(self, file, reference_format=None):
        """Process uploaded file"""
        try:
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()
            
            # Read and process file
            if ext in self.supported_formats['excel']:
                df = pd.read_excel(file)
                data = df.to_dict(orient='records')
            elif ext in self.supported_formats['csv']:
                df = pd.read_csv(file)
                data = df.to_dict(orient='records')
            else:
                raise ValueError(f"Unsupported file format: {ext}")

            return self.process_data(data, reference_format)

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise
            
    def _apply_reference_format(self, data, reference_format):
        """Apply reference JSON format structure to the data"""
        if isinstance(reference_format, str):
            reference_format = json.loads(reference_format)
            
        formatted_data = {}
        for key, value in reference_format.items():
            if isinstance(value, dict):
                formatted_data[key] = self._apply_reference_format(data, value)
            else:
                formatted_data[key] = data.get(key, "")
        return formatted_data

    def save_output_file(self, data, output_format='.txt'):
        """Save processed data to a file"""
        try:
            if output_format == '.txt':
                # Save JSON to text file
                filename = f"converted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                return filename
        except Exception as e:
            logger.error(f"Error saving output file: {str(e)}")
            raise
