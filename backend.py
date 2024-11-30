from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import spacy
from typing import Dict
import logging
import re

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure the Gemini API key
genai.configure(api_key="AIzaSyC6KNcF2_wr5CLft6p-WFra7Yo5UrYBm1E")

# Load spaCy language model for NER
nlp = spacy.load("en_core_web_sm")


# Define a Pydantic model for user input
class ChatInput(BaseModel):
    message: str
    user_id: str = "dummy_user"  # Default user_id for now


# Dictionary to store user context
user_context: Dict[str, Dict] = {}

# Select an available model
model_name = "gemini-1.5-flash"
model = genai.GenerativeModel(model_name=model_name)


# Helper function to extract entities dynamically using spaCy and regex
def extract_entities(message: str) -> Dict[str, str]:
    doc = nlp(message)
    extracted_entities = {}

    # Extract location and dates using spaCy
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical entity (e.g., cities, countries)
            extracted_entities["location"] = ent.text
        elif ent.label_ == "DATE":  # Dates
            extracted_entities["dates"] = ent.text

    # Extract budget using regex
    budget_match = re.search(r"\$\d+|\d+\s?(USD|EUR|INR|GBP)", message, re.IGNORECASE)
    if budget_match:
        extracted_entities["budget"] = budget_match.group()

    # Extract travel companions
    if "solo" in message.lower():
        extracted_entities["companions"] = "solo"
    elif "partner" in message.lower():
        extracted_entities["companions"] = "partner"
    elif "family" in message.lower():
        extracted_entities["companions"] = "family"
    elif "friends" in message.lower():
        extracted_entities["companions"] = "friends"

    # Extract accommodation preferences
    if "hotel" in message.lower():
        extracted_entities["accommodation"] = "hotel"
    elif "airbnb" in message.lower():
        extracted_entities["accommodation"] = "Airbnb"
    elif "hostel" in message.lower():
        extracted_entities["accommodation"] = "hostel"

    # Extract interests
    interests = []
    if "museums" in message.lower():
        interests.append("museums")
    if "shopping" in message.lower():
        interests.append("shopping")
    if "food" in message.lower():
        interests.append("food")
    if "historical sites" in message.lower():
        interests.append("historical sites")
    if "nightlife" in message.lower():
        interests.append("nightlife")
    if interests:
        extracted_entities["interests"] = ", ".join(interests)

    return extracted_entities


# Define the chat endpoint
@app.post("/chat")
async def chat_with_bot(chat_input: ChatInput):
    user_id = chat_input.user_id
    user_message = chat_input.message

    logging.debug("Incoming Message: %s", user_message)

    # Retrieve or initialize user context
    context = user_context.get(user_id, {})

    # Extract entities dynamically
    entities = extract_entities(user_message)
    context.update(entities)  # Update context with extracted entities

    # Format context as a string to include in the message
    context_string = (
        f"Location: {context.get('location', 'unknown')}, "
        f"Dates: {context.get('dates', 'unknown')}, "
        f"Budget: {context.get('budget', 'unknown')}, "
        f"Companions: {context.get('companions', 'unknown')}, "
        f"Accommodation: {context.get('accommodation', 'unknown')}, "
        f"Interests: {context.get('interests', 'unknown')}. "
    )

    # Start a chat session
    try:
        # Initialize the chat session
        chat = model.start_chat()

        # Include the role definition in the first message sent to the bot
        role_prompt = (
            "You are a travel assistant bot. Respond only with travel-related "
            "information and advice. The travel duration is strictly for 1 day ONLY. "
            "Provide specific activities, timing, and tips for the one-day trip."
        )
        response = chat.send_message(f"{role_prompt} {context_string} {user_message}")
        answer = response.text

        # Save updated context
        user_context[user_id] = context

        # Include context in the response
        return {"response": answer, "context": context}
    except Exception as e:
        logging.error("Unexpected Error: %s", str(e))
        return {"error": str(e)}


# To run the app directly if this file is executed
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
