import os
from dotenv import load_dotenv
from openai import OpenAI

def load_api_key():
    """Load the API key from environment variables."""
    load_dotenv()
    return os.getenv("AI_KEY")

def initialize_client():
    """Initialize the OpenAI client with the API key."""
    key = load_api_key()
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

def send_prompt(model, messages):
    """Send a prompt to the LLM and return the response."""
    # Initialize the client
    client = initialize_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content
