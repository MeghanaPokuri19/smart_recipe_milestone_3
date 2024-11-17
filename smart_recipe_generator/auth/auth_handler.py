import sys
import os
import hashlib
import streamlit as st
from db.database import connect_db

# Add the root project directory to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    record = cursor.fetchone()
    conn.close()
    if record and record[0] == hash_password(password):
        return True
    return False

def register_user(username, password, phone_number, email, profile_picture):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, phone_number, email, profile_picture) VALUES (%s, %s, %s, %s, %s)",
            (username, hash_password(password), phone_number, email, profile_picture.read())
        )
        conn.commit()
        return True
    except Exception as e:
        print("Registration error:", e)
        return False
    finally:
        conn.close()
