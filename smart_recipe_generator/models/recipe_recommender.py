import sys
import os
import openai
from config import OPENAI_API_KEY
from db.database import connect_db

# Add the root project directory to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

openai.api_key = OPENAI_API_KEY

def generate_recipe_suggestion(ingredients, diet_preference):
    prompt = f"Suggest a {diet_preference} recipe using the following ingredients: {', '.join(ingredients)}"
    
    # Update the API call to use gpt-3.5-turbo, which requires `messages` instead of `prompt`
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for generating recipes."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the response text
    return response.choices[0].message["content"].strip()

def save_recipe(username, recipe_name, ingredients, instructions, diet_preference):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipes (username, recipe_name, ingredients, instructions, diet_preference)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, recipe_name, ', '.join(ingredients), instructions, diet_preference))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving recipe: {e}")
        return False
    finally:
        conn.close()
