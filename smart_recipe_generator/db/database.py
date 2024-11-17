import psycopg2

def connect_db():
    conn = psycopg2.connect(
        host="localhost",
        database="recipe",
        user="postgres",
        password="ironmanttt"  # Update with your actual password
    )
    return conn
