import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    config = {
        'host': '34.142.254.175',  
        'user': 'root',
        'password': 'ILOVESUSHI123!',
        'database': 'internchatbot',
        'port': 3306
    }
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if query.lower().startswith('select'):
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return cursor.rowcount
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if connection.is_connected():
                connection.close()

def create_user(email, password):
    # Check if email already exists
    check_query = "SELECT email FROM users WHERE email = %s"
    result = execute_query(check_query, (email,))
    
    if result:
        return False, "Email already exists"
    
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Insert new user
    insert_query = """
    INSERT INTO users (email, password, role, created_at) 
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        current_time = datetime.now()
        params = (email, hashed_password, 'user', current_time)
        rows_affected = execute_query(insert_query, params)
        
        if rows_affected:
            return True, "User created successfully"
        return False, "Failed to create user"
    except Error as e:
        return False, str(e)