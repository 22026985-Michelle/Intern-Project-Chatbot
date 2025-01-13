import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db_connection():
    config = {
        'host': '34.142.254.175',
        'user': 'root',
        'password': 'ILOVESUSHI123!',
        'database': 'internchatbot',
        'port': 3306,
        'connect_timeout': 30,
        'use_pure': True,
        'allow_local_infile': True,
        'auth_plugin': 'mysql_native_password'
    }
    
    try:
        logger.info(f"Attempting to connect to MySQL at {config['host']}:{config['port']}")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Successfully connected to MySQL. Server version: {db_info}")
            return connection
        
    except Error as e:
        logger.error(f"Error connecting to MySQL: {str(e)}")
        return None

def execute_query(query, params=None):
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to connect to the database")
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.rowcount
    except Error as e:
        logger.error(f"Database query error: {e}")
        raise  # Re-raise the error for debugging
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
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
    """Create a new chat and move existing 'Now' chats to 'Recents'"""
    try:
        connection = get_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor(dictionary=True)
        
        # First move existing 'Now' chats to 'Recents'
        move_query = """
        UPDATE chats 
        SET section = 'Recents',
            updated_at = NOW()
        WHERE user_id = %s AND section = 'Now'
        """
        cursor.execute(move_query, (user_id,))
        
        # Then create the new chat
        insert_query = """
        INSERT INTO chats (user_id, section, created_at, updated_at)
        VALUES (%s, 'Now', NOW(), NOW())
        """
        cursor.execute(insert_query, (user_id,))
        chat_id = cursor.lastrowid
        
        # Cleanup old chats if needed
        count_query = "SELECT COUNT(*) as chat_count FROM chats WHERE user_id = %s"
        cursor.execute(count_query, (user_id,))
        result = cursor.fetchone()
        
        if result and result['chat_count'] > 100:
            cleanup_old_chats(user_id, keep_count=95)
            
        connection.commit()
        return chat_id
        
    except Error as e:
        logger.error(f"Error in create_new_chat: {str(e)}")
        if connection:
            connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
def add_message(chat_id, content, is_user=True):
    """Add a message to a chat session"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            return False

        cursor = connection.cursor(dictionary=True)
        
        # Add message
        message_query = """
        INSERT INTO messages (chat_id, content, is_user, created_at)
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(message_query, (chat_id, content, is_user))
        
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
    
def get_recent_chats(user_id):
    """Get chats for a user, separated by section"""
    query = """
    SELECT 
        c.chat_id,
        COALESCE(c.title, 'New Chat') as title,
        c.section,
        c.created_at,
        c.updated_at,
        c.is_starred,
        (SELECT content 
         FROM messages m 
         WHERE m.chat_id = c.chat_id 
         ORDER BY created_at DESC 
         LIMIT 1) as last_message
    FROM chats c
    WHERE c.user_id = %s
    ORDER BY 
        CASE 
            WHEN c.section = 'Now' THEN 1
            WHEN c.section = 'Recents' THEN 2
            ELSE 3
        END,
        c.updated_at DESC
    """
    return execute_query(query, (user_id,))

def move_chat_to_recents(chat_id):
    """Move a chat to the Recents section"""
    update_query = """
    UPDATE chats 
    SET section = 'Recents', 
        updated_at = NOW() 
    WHERE chat_id = %s
    """
    return execute_query(update_query, (chat_id,))

def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    query = """
    SELECT content, is_user, created_at
    FROM messages
    WHERE chat_id = %s
    ORDER BY created_at ASC
    """
    return execute_query(query, (chat_id,))

def cleanup_old_chats(user_id, keep_count=5):
    query = """
    DELETE FROM chats 
    WHERE chat_id NOT IN (
        SELECT chat_id 
        FROM chats 
        WHERE user_id = %s 
        ORDER BY updated_at DESC 
        LIMIT %s
    )
    """
    execute_query(query, (user_id, keep_count))


def get_user_by_email(email):
    """Get user details by email"""
    logger.info(f"Looking up user with email: {email}")
    query = "SELECT user_id, username, email, role FROM users WHERE email = %s"
    result = execute_query(query, (email,))
    logger.info(f"User lookup result: {result}")
    return result[0] if result else None

