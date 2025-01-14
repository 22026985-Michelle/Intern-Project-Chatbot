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
    logger.info(f"Creating new chat for user_id: {user_id}")
    
    try:
        connection = get_db_connection()
        if not connection:
            logger.error("Failed to establish database connection")
            return None

        cursor = connection.cursor(dictionary=True)
        
        # Check chat count
        count_query = "SELECT COUNT(*) as chat_count FROM chats WHERE user_id = %s"
        cursor.execute(count_query, (user_id,))
        count_result = cursor.fetchone()
        
        if count_result and count_result['chat_count'] >= 5:
            # Keep only the 4 most recent chats
            cleanup_old_chats(user_id, keep_count=4)
        
        # Insert new chat
        insert_query = """
        INSERT INTO chats (user_id, created_at, updated_at, section, title)
        VALUES (%s, NOW(), NOW(), 'Now', 'New Chat')
        """
        cursor.execute(insert_query, (user_id,))
        chat_id = cursor.lastrowid
        
        connection.commit()
        logger.info(f"Successfully created chat with ID: {chat_id}")
        return chat_id
        
    except Exception as e:
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
    
def get_recent_chats(user_id, limit=5):
    """Get recent chats for a user"""
    query = """
    SELECT c.chat_id, 
           COALESCE(c.title, 'New Chat') as title,
           c.section,
           c.created_at,
           c.updated_at,
           (SELECT content 
            FROM messages m 
            WHERE m.chat_id = c.chat_id 
            ORDER BY created_at DESC 
            LIMIT 1) as last_message
    FROM chats c
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

def cleanup_old_chats(user_id, keep_count=4):
    """Delete old chats while keeping the specified number of most recent ones"""
    try:
        delete_query = """
        DELETE FROM chats 
        WHERE chat_id IN (
            SELECT chat_id FROM (
                SELECT chat_id
                FROM chats 
                WHERE user_id = %s 
                ORDER BY updated_at DESC 
                LIMIT 100 OFFSET %s
            ) tmp
        )
        """
        execute_query(delete_query, (user_id, keep_count))
    except Exception as e:
        logger.error(f"Error in cleanup_old_chats: {str(e)}")


def get_user_by_email(email):
    """Get user details by email"""
    logger.info(f"Looking up user with email: {email}")
    query = "SELECT user_id, username, email, role FROM users WHERE email = %s"
    result = execute_query(query, (email,))
    logger.info(f"User lookup result: {result}")
    return result[0] if result else None