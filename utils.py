import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (API keys) securely from the .env file
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq client only if the API key exists
groq_client = Groq(api_key=groq_key) if groq_key else None

def load_data():
    """
    Reads the local JSON database. 
    If the file doesn't exist yet (first run), it returns a default empty structure.
    """
    try:
        with open("database.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"routine": [], "sessions": []}

def save_data(data):
    """
    Writes the updated data dictionary back to the JSON file.
    Using indent=4 makes the JSON file human-readable.
    """
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

def get_ai_tip(current_workout, past_sessions):
    """
    Generates a personalized coaching tip using the Groq API.
    This is a generator function (uses yield) to support live text streaming in Streamlit.
    """
    if not groq_client:
        yield "Error: Groq API key missing in .env file."
        return

    # Context Management: We only send the last 3 sessions to the AI.
    # This prevents the prompt from getting too large (saving tokens and maintaining speed).
    history_text = ""
    if past_sessions:
        history_text = "\nHere is my workout history:\n"
        for session in past_sessions[-3:]:
            history_text += f"Date: {session['date']} - {session['exercises']}\n"

    # Prompt Engineering: Giving the AI a specific persona and clear constraints.
    prompt = f"You are an expert personal trainer. Here is my workout today: {current_workout}\n{history_text}\nGive me one short tip (max 2 sentences)."

    try:
        # We use stream=True so the UI can display the text as it's generated
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert personal trainer."},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-120b",
            stream=True,
            temperature=0.7, # Balances creativity and focus
            max_tokens=500
        )
        
        # Yield chunks of text as they arrive from the API
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Groq Error: {e}"