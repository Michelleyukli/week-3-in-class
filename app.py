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

def add_or_update_prompt(title, text, favorite):
    # Check if the prompt exists
    with connect_db() as con:
        with con.cursor() as cur:
            # Attempt to update if the prompt already exists (assumes title is unique)
            cur.execute("UPDATE prompts SET prompt = %s, favorite = %s WHERE title = %s RETURNING id", (text, favorite, title))
            if cur.rowcount == 0:
                # Insert new prompt if not existing
                cur.execute("INSERT INTO prompts (title, prompt, favorite) VALUES (%s, %s, %s)", (title, text, favorite))
            con.commit()

def display_prompts():
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute("SELECT id, title, prompt, favorite FROM prompts")
            prompts = cur.fetchall()
            for prompt in prompts:
                with st.expander(f"{prompt['title']} {'(Favorite)' if prompt['favorite'] else ''}"):
                    st.text_area("Prompt", value=prompt['prompt'], key=f"{prompt['id']}_text")
                    if st.button("Save", key=f"{prompt['id']}_save"):
                        update_text = st.session_state[f"{prompt['id']}_text"]
                        add_or_update_prompt(prompt['title'], update_text, prompt['favorite'])
                    if st.button("Delete", key=f"{prompt['id']}_delete"):
                        delete_prompt(prompt['id'])
                    if st.button("Toggle Favorite", key=f"{prompt['id']}_fav"):
                        toggle_favorite(prompt['id'], not prompt['favorite'])

def delete_prompt(prompt_id):
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
            con.commit()

def toggle_favorite(prompt_id, new_status):
    with connect_db() as con:
        with con.cursor() as cur:
            cur.execute("UPDATE prompts SET favorite = %s WHERE id = %s", (new_status, prompt_id))
            con.commit()

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
            st.success("Prompt saved!")

    # Display and manage existing prompts
    display_prompts()

if __name__ == "__main__":
    main()
