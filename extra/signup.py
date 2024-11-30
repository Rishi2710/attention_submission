import streamlit as st
import hashlib
import sqlite3

# Database setup
conn = sqlite3.connect("users.db")
c = conn.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
    conn.commit()


def add_user(username, password):
    c.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
    )
    conn.commit()


def main():
    st.title("Sign Up for Travel Bot")
    create_table()

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            add_user(username, hashed_password)
            st.success("Account created successfully! Please [login](login.py).")
        else:
            st.error("Passwords do not match!")


if __name__ == "__main__":
    main()
