from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Connect to Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# Define a Pydantic model for user input
class UserMessage(BaseModel):
    user_id: str = "dummy_user"  # Default to dummy user_id
    message: str


# Utility functions to interact with Neo4j
def save_context(user_id: str, key: str, value: str):
    """Save or update context in Neo4j."""
    with driver.session() as session:
        session.run(
            """
            MERGE (u:User {id: $user_id})
            SET u[$key] = $value
            """,
            user_id=user_id,
            key=key,
            value=value,
        )


def get_context(user_id: str):
    """Retrieve all context for a user from Neo4j."""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN properties(u) AS context
            """,
            user_id=user_id,
        )
        record = result.single()
        return record["context"] if record else {}


# Define the chatbot endpoint
@app.post("/chat")
async def chat_with_user(user_message: UserMessage):
    user_id = user_message.user_id
    message = user_message.message

    # Retrieve all context for the user
    context = get_context(user_id)

    # Check for keywords to identify the intent or topic
    if "planning" in message.lower():
        context["topic"] = "planning"
        save_context(user_id, "topic", "planning")
        response = "Great! What are you planning? Please provide details."
    elif "recommendation" in message.lower():
        context["topic"] = "recommendation"
        save_context(user_id, "topic", "recommendation")
        response = "What kind of recommendations are you looking for?"
    else:
        # Generate a response based on stored context
        if "topic" in context:
            if context["topic"] == "planning":
                response = "You're currently planning something. Let me know your requirements."
            elif context["topic"] == "recommendation":
                response = (
                    "You're looking for recommendations. Can you specify what type?"
                )
            else:
                response = "I'm not sure what you're asking. Could you clarify?"
        else:
            response = "I couldn't identify the context. Can you tell me what you're looking for?"

    return {"response": response}


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
