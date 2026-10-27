from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
print("Key:", os.getenv("GROQ_API_KEY")[:10]) # Should print your key

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Connecting to Groq...")

completion = client.chat.completions.create(
    messages=[{"role": "user", "content": "Say 'I am fast!'"}],
    model="openai/gpt-oss-120b",
)

print("Response:", completion.choices[0].message.content)