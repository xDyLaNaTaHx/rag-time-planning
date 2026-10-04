import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the client
key = os.getenv("AI_KEY")
client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

# Send a prompt to the LLM
response = client.chat.completions.create(
    model=os.getenv("AI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain recursion in simple terms."}
    ]
)

# Print the output text
print(response.choices[0].message.content)
