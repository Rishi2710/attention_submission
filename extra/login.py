import streamlit as st
import sqlite3
import hashlib

# Database setup
conn = sqlite3.connect("users.db")
c = conn.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.commit()


def authenticate_user(username, password):
    c.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
    )
    return c.fetchone()


def main():
    st.title("Login to PathPal")
    create_table()

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user = authenticate_user(username, hashed_password)
            if user:
                st.success("Login successful! Redirecting to PathPal...")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.experimental_rerun()  # Reload to check login state
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password.")

    # Redirect to app.py if already logged in
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.experimental_rerun()  # Redirect to app.py

    st.markdown("Don't have an account? [Sign up here](signup.py)")


if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    main()
