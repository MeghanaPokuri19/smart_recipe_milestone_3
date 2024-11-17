import sys
import os
from config import DATABASE_CONFIG
import psycopg2

# Add the root project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def populate_user_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(64) NOT NULL,
            phone_number VARCHAR(15),
            email VARCHAR(255),
            profile_picture BYTEA
        );
    """)

    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            recipe_name TEXT,
            ingredients TEXT,
            instructions TEXT,
            diet_preference VARCHAR(10),
            FOREIGN KEY (username) REFERENCES users (username)
        );
    """)
    conn.commit()
    print("User and Recipes tables created.")
    conn.close()

if __name__ == "__main__":
    populate_user_db()
