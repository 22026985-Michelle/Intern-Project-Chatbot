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
    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                logger.debug(f"Executing query: {query} with params: {params}")
                cursor.execute(query, params)
                if query.lower().startswith('select'):
                    result = cursor.fetchall()
                    logger.debug(f"Query result: {result}")
                    return result
                else:
                    connection.commit()
                    logger.debug(f"Query affected {cursor.rowcount} rows")
                    return cursor.rowcount
        except Error as e:
            logger.error(f"Error executing query: {str(e)}")
            return None
        finally:
            if connection.is_connected():
                connection.close()
                logger.debug("Database connection closed")

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
    query = """
    INSERT INTO chats (user_id, created_at, updated_at)
    VALUES (%s, NOW(), NOW())
    """
    execute_query(query, (user_id,))
    
    # Get the created chat_id
    get_chat_query = """
    SELECT chat_id FROM chats 
    WHERE user_id = %s 
    ORDER BY created_at DESC 
    LIMIT 1
    """
    result = execute_query(get_chat_query, (user_id,))
    return result[0]['chat_id'] if result else None

def add_message(chat_id, content, is_user=True):
    """Add a message to a chat session"""
    query = """
    INSERT INTO messages (chat_id, content, is_user, created_at)
    VALUES (%s, %s, %s, NOW())
    """
    execute_query(query, (chat_id, content, is_user))
    
    # Update chat's updated_at timestamp
    update_query = """
    UPDATE chats SET updated_at = NOW()
    WHERE chat_id = %s
    """
    execute_query(update_query, (chat_id,))

def get_recent_chats(user_id, limit=10):
    """Get recent chats for a user"""
    query = """
    SELECT c.chat_id, 
           m.content as last_message,
           c.created_at,
           c.updated_at
    FROM chats c
    LEFT JOIN messages m ON c.chat_id = m.chat_id
    WHERE c.user_id = %s
    ORDER BY c.updated_at DESC
    LIMIT %s
    """
    return execute_query(query, (user_id, limit))

def get_chat_messages(chat_id):
    """Get all messages for a specific chat"""
    query = """
    SELECT content, is_user, created_at
    FROM messages
    WHERE chat_id = %s
    ORDER BY created_at ASC
    """
    return execute_query(query, (chat_id,))

def cleanup_old_chats(user_id, keep_count=10):
    """Remove old chats keeping only the most recent ones"""
    query = """
    DELETE FROM chats 
    WHERE chat_id IN (
        SELECT chat_id FROM (
            SELECT chat_id 
            FROM chats 
            WHERE user_id = %s 
            ORDER BY updated_at DESC 
            LIMIT 1000 OFFSET %s
        ) as old_chats
    )
    """
    execute_query(query, (user_id, keep_count))