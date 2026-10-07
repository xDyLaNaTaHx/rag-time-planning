import os
from llm import send_prompt

response = send_prompt(
    model=os.getenv("AI_MODEL"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain recursion in simple terms."}
    ]
)

# Print the output text
print(response)
