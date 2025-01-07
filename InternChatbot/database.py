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

def create_user(email, password):
    logger.info(f"Attempting to create user with email: {email}")
    
    # Check if email already exists
    check_query = "SELECT email FROM users WHERE email = %s"
    result = execute_query(check_query, (email,))
    
    if result:
        logger.info(f"User with email {email} already exists")
        return False, "Email already exists"
    
    # Insert new user
    insert_query = """
    INSERT INTO users (email, password, role, created_at) 
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        current_time = datetime.now()
        params = (email, password, 'user', current_time)
        rows_affected = execute_query(insert_query, params)
        
        if rows_affected:
            logger.info(f"Successfully created user with email {email}")
            return True, "User created successfully"
        logger.error(f"Failed to create user with email {email}")
        return False, "Failed to create user"
    except Error as e:
        logger.error(f"Error creating user: {str(e)}")
        return False, str(e)