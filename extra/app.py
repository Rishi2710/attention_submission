import streamlit as st
import requests

# Backend URL for the chatbot
backend_url = "http://127.0.0.1:8001/chat"


def main():
    # Check if the user is logged in
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("You are not logged in. Redirecting to login page...")
        st.stop()  # Stops execution if the user is not logged in

    # Greet the logged-in user
    st.title("PathPal")
    st.write("Wherever you go, I’ll guide the way!")
    st.write(f"Welcome, {st.session_state['username']}!")

    # Logout button
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()  # Redirect to login.py

    # Chatbot UI
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_message = st.text_input("Your message")

    # Send message and display response
    if st.button("Send"):
        if user_message:
            try:
                # Send user message to backend
                response = requests.post(
                    backend_url, json={"message": user_message}
                ).json()
                if "response" in response:
                    bot_response = response["response"]
                    # Save user message and bot response in chat history
                    st.session_state.chat_history.append(
                        {"user": user_message, "bot": bot_response}
                    )
                else:
                    st.error("Error: " + response.get("error", "Unknown error"))
            except requests.exceptions.ConnectionError:
                st.error("Backend is not running. Please start the FastAPI server.")
        else:
            st.warning("Please enter a message!")

    # Display chat history with styled blocks
    st.write("### Chat History")
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


if __name__ == "__main__":
    main()
