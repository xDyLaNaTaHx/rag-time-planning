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


def send_prompt(model, messages, json_mode: bool = False):
    """Send a prompt to the LLM and return the response text."""
    client = initialize_client()
    kwargs = {
        "model": model,
        "messages": messages,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
