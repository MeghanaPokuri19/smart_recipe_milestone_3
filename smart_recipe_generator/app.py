import streamlit as st
from utils.image_processing import load_image, preprocess_image
from utils.ocr_tool import perform_ocr
from models.recipe_recommender import generate_recipe_suggestion
from db.database import connect_db
from auth.auth_handler import authenticate_user, register_user
from PIL import Image
import base64
import io
import os

# Set up page with custom title and layout
st.set_page_config(page_title="Smart Recipe Generator", layout="centered")

# CSS for background image using base64 encoding
def add_fullscreen_background_image():
    # Update the path to your background image
    img_path = r"C:\Users\parva\OneDrive\Desktop\smart recipe generator\smart_recipe_generator\static\background.jpg"
    
    # Read and encode the image in base64 format
    with open(img_path, "rb") as image_file:
        img_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Inject CSS with base64 image embedded
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{img_data}");
                background-size: cover;
                color: white;
            }}
            .content-container {{
                max-width: 600px;
                margin: auto;
            }}
            .st-title {{
                font-size: 2rem;
                font-weight: bold;
                color: #ffffff;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Initialize session state flags
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# Function to render login, signup, and main app pages
def main():
    add_fullscreen_background_image()
    if st.session_state.logged_in:
        recipe_generator_page()
    elif st.session_state.show_signup:
        signup_page()
    else:
        login_page()

def login_page():
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.title("Welcome to Smart Recipe Generator")
        st.markdown('<p class="title">Log in to get started</p>', unsafe_allow_html=True)

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username  # Store username in session
                st.success("Logged in successfully!")
                st.session_state.show_signup = False
            else:
                st.error("Invalid username or password.")

        if st.button("Sign Up", key="signup_button"):
            st.session_state.show_signup = True
        st.markdown('</div>', unsafe_allow_html=True)

def signup_page():
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.title("Create a New Account")

        username = st.text_input("Choose a Username", key="signup_username")
        phone_number = st.text_input("Phone Number", key="signup_phone")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        profile_picture = st.file_uploader("Upload Profile Picture", type=["jpg", "png"], key="signup_profile_pic")

        if st.button("Register", key="register_button"):
            success = register_user(username, password, phone_number, email, profile_picture)
            if success:
                st.success("Account created successfully! Please log in.")
                st.session_state.show_signup = False
            else:
                st.error("Error creating account.")

        if st.button("Back to Login", key="back_to_login"):
            st.session_state.show_signup = False
        st.markdown('</div>', unsafe_allow_html=True)

def fetch_user_profile(username):
    # Fetch user details from the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, phone_number, email, profile_picture FROM users WHERE username = %s", (username,))
    record = cursor.fetchone()
    conn.close()
    
    if record:
        return {
            "username": record[0],
            "phone_number": record[1],
            "email": record[2],
            "profile_picture": record[3]
        }
    return None

def display_user_profile_sidebar():
    # Display user profile details in the sidebar
    st.sidebar.header("User Profile")
    user_profile = fetch_user_profile(st.session_state.username)
    
    if user_profile:
        st.sidebar.write(f"**Username:** {user_profile['username']}")
        st.sidebar.write(f"**Phone Number:** {user_profile['phone_number']}")
        st.sidebar.write(f"**Email:** {user_profile['email']}")
        
        if user_profile["profile_picture"]:
            try:
                profile_image = Image.open(io.BytesIO(user_profile["profile_picture"]))
                st.sidebar.image(profile_image, caption="Profile Picture", width=100)
            except Exception as e:
                st.sidebar.write("Failed to load profile picture.")
                st.sidebar.write(str(e))
        else:
            st.sidebar.write("No profile picture available.")
        
        if st.sidebar.button("Logout"):
            # Clear the session state for logout
            st.session_state.logged_in = False
            st.session_state.show_signup = False
            # Use query parameters to trigger a reload
            st.experimental_set_query_params()  # Clears any query params, which triggers a reload
    else:
        st.sidebar.write("Failed to load profile details.")

# Function to save recipe to the database
def save_recipe(username, recipe_name, ingredients, instructions, diet_preference):
    conn = connect_db()
    cursor = conn.cursor()

    # Check if the username exists in the users table
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user is None:
        st.error(f"User {username} does not exist. Please sign up first.")
        conn.close()
        return

    try:
        # Insert the recipe if the user exists
        cursor.execute(
            "INSERT INTO recipes (username, recipe_name, ingredients, instructions, diet_preference) VALUES (%s, %s, %s, %s, %s)",
            (username, recipe_name, ",".join(ingredients), instructions, diet_preference)
        )
        conn.commit()
        st.success("Recipe saved successfully!")
        print(f"Recipe saved: {recipe_name}, Ingredients: {ingredients}")  # Debugging log
    except Exception as e:
        st.error(f"Error saving recipe: {e}")
        print(f"Error saving recipe: {e}")
    finally:
        conn.close()

# Function to fetch saved recipes for the user
def get_saved_recipes(username):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT recipe_name, ingredients, instructions, diet_preference FROM recipes WHERE username = %s", (username,))
        recipes = cursor.fetchall()
        print(f"Fetched recipes for {username}: {recipes}")  # Debugging log
        if recipes:
            return recipes
        else:
            st.write("No saved recipes found.")
    except Exception as e:
        st.error(f"Error fetching saved recipes: {e}")
        print(f"Error fetching saved recipes: {e}")
    finally:
        conn.close()
    return []


def recipe_generator_page():
    display_user_profile_sidebar()
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.title("Smart Recipe Generator")
        
        st.write("Upload one or more images of ingredients to get recipe suggestions.")
        uploaded_files = st.file_uploader("Choose images...", accept_multiple_files=True, key="recipe_images")

        # Add radio buttons for Veg/Non-Veg preferences
        diet_preference = st.radio("Select Diet Preference", ["Veg", "Non-Veg"], key="diet_preference")

        if st.button("Get Recipe", key="get_recipe_button"):
            ingredients = []
            for file in uploaded_files:
                img_path = f"assets/sample_images/{file.name}"
                with open(img_path, "wb") as f:
                    f.write(file.getbuffer())
                recognized_text = perform_ocr(img_path)
                ingredients.append(recognized_text)

            recipe = generate_recipe_suggestion(ingredients, diet_preference)
            st.write("Generated Recipe:", recipe)

            # Option to save the recipe
            if st.button("Save Recipe", key="save_recipe_button"):
                recipe_name = f"Recipe based on {', '.join(ingredients)}"
                instructions = "Your recipe instructions go here."  # You could ask for instructions or use GPT for them.
                save_recipe(st.session_state.username, recipe_name, ingredients, instructions, diet_preference)
        
        # View saved recipes
        if st.button("View Saved Recipes", key="view_saved_recipes_button"):
            saved_recipes = get_saved_recipes(st.session_state.username)
            if saved_recipes:
                st.subheader("Your Saved Recipes:")
                for recipe in saved_recipes:
                    st.write(f"**{recipe[0]}**")
                    st.write(f"Ingredients: {recipe[1]}")
                    st.write(f"Instructions: {recipe[2]}")
                    st.write(f"Diet Preference: {recipe[3]}")
                    st.markdown("---")
            else:
                st.write("No saved recipes found.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
