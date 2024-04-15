import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import streamlit as st

load_dotenv()  # Ensure the environment variables are loaded

def connect_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        st.error("Database URL is not set.")
        raise ValueError("DATABASE_URL is not set in environment variables")
    try:
        con = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return con
    except psycopg2.OperationalError as e:
        st.error(f"Failed to connect to the database: {e}")
        raise

# Ensure database table is created
def setup_db():
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    favorite BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.commit()

# Add streamlit widgets and handlers for CRUD operations, searching, and filtering
def main():
    st.title("ChatGPT Prompt Manager")
    setup_db()

    # Add form to create/update prompts
    with st.form("prompt_form"):
        title = st.text_input("Title")
        prompt_text = st.text_area("Prompt")
        favorite = st.checkbox("Favorite")
        submit = st.form_submit_button("Save Prompt")
        if submit and title and prompt_text:
            add_or_update_prompt(title, prompt_text, favorite)

    # Display and manage existing prompts
    display_prompts()

def add_or_update_prompt(title, text, favorite):
    # Function to add or update prompts in the database
    pass

def display_prompts():
    # Function to display prompts with options to edit, delete, and mark as favorite
    pass

if __name__ == "__main__":
    main()
