import streamlit as st
import sqlite3
import hashlib
import requests

# Backend URL for the chatbot
backend_url = "http://127.0.0.1:8001/chat"

# Database setup
conn = sqlite3.connect("users.db")
c = conn.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.commit()


def add_user(username, password):
    c.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
    )
    conn.commit()


def authenticate_user(username, password):
    c.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
    )
    return c.fetchone()


# Login page
def login_page():
    st.title("Login to PathPal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user = authenticate_user(username, hashed_password)
            if user:
                st.success("Login successful!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "app"
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password.")

    st.markdown("Don't have an account? [Sign up here](#signup-page)")
    st.session_state["page"] = (
        "signup" if st.button("Go to Signup") else st.session_state.get("page", "login")
    )


# Signup page
def signup_page():
    st.title("Sign Up for PathPal")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            add_user(username, hashed_password)
            st.success("Account created successfully! Please log in.")
            st.session_state["page"] = "login"
            st.experimental_rerun()
        else:
            st.error("Passwords do not match!")

    st.markdown("Already have an account? [Login here](#login-page)")
    st.session_state["page"] = (
        "login" if st.button("Go to Login") else st.session_state.get("page", "signup")
    )


# Chatbot app page
def app_page():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("You are not logged in. Redirecting to login page...")
        st.session_state["page"] = "login"
        st.experimental_rerun()

    st.title("PathPal")
    st.write("Wherever you go, I’ll guide the way!")
    st.write(f"Welcome, {st.session_state['username']}!")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"
        st.experimental_rerun()

    # Chat functionality
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_message = st.text_input("Your message")

    if st.button("Send"):
        if user_message:
            try:
                response = requests.post(
                    backend_url, json={"message": user_message}
                ).json()
                if "response" in response:
                    bot_response = response["response"]
                    st.session_state.chat_history.append(
                        {"user": user_message, "bot": bot_response}
                    )
                else:
                    st.error("Error: " + response.get("error", "Unknown error"))
            except requests.exceptions.ConnectionError:
                st.error("Backend is not running. Please start the FastAPI server.")
        else:
            st.warning("Please enter a message!")

    for chat in st.session_state.chat_history:
        st.markdown(
            f"""
            <div>
                <strong>You:</strong> {chat['user']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="background: grey; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <strong>PathPal:</strong> {chat['bot']}
            </div>
            """,
            unsafe_allow_html=True,
        )


# Navigation logic
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "signup":
        signup_page()
    elif st.session_state["page"] == "app":
        app_page()


if __name__ == "__main__":
    create_table()
    main()
