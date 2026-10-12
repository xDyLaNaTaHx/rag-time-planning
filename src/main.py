import os
from dotenv import load_dotenv
from llm import send_prompt
import chromadb

load_dotenv()

# Initialize the Chroma client and create a collection for user support documents
chroma_client = chromadb.Client()
user_support_collection = chroma_client.create_collection(
    name="user-support"
)

user_support_collection.add(
   ids=["1", "2", "3", "4"],
   documents=[
        "I want to learn how to code in Python.",
        "I want to learn 1 song on guitar.",
        "I want to squat 200lbs.",
        "I work from 6am to 8pm every Monday to Thursday."
   ]
)

user_query = "How should I schedule my week?"

results = user_support_collection.query(
    query_texts=[user_query],
    n_results=4
)
context = "\n".join(results["documents"][0])

prompt = f"How should I schedule my week based on the following context: {context}"

response = send_prompt(
    model=os.getenv("AI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful calendar assistant."},
        {"role": "user", "content": prompt}
    ]
)

# Print the output text
print(response)
