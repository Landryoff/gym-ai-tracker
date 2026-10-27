# 🏋️ AI-Powered Gym Tracker

A personal fitness application built to track workouts, manage routines, and receive personalized AI coaching tips based on workout history.

## 🎯 The Problem
Standard fitness apps are either overly complex or don't provide actionable, personalized feedback. This project was built to demonstrate how to integrate a Large Language Model (LLM) into a standard CRUD (Create, Read, Update, Delete) application to provide real-time, contextual coaching.

## ✨ Features
- **Interactive UI:** Multi-tab layout (Current Session, History, Routine) built with Streamlit.
- **Data Management:** Local JSON database with date-merging logic (multiple workouts on the same day are combined).
- **Dynamic Grids:** Pandas DataFrames used for editable, clean data tables.
- **AI Coach:** Integrated with Groq API (using the Llama-3 model) to analyze the current workout against the last 3 sessions and generate a personalized tip.
- **Secure:** API keys are managed via `.env` and protected with `.gitignore`.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Data Handling:** Pandas, JSON
- **AI Integration:** Groq API (OpenAI-compatible endpoint)
- **Environment Management:** Python-dotenv

## 🏗️ Architecture
The project is split into two main files to separate concerns:
- `app.py`: Handles all UI rendering, session state, and layout logic.
- `utils.py`: Handles the backend logic, including reading/writing to the JSON database and making asynchronous streaming API calls to the Groq LLM.

## 🚀 How to Run Locally
1. Clone the repository.
2. Install dependencies: `pip install streamlit pandas groq python-dotenv`
3. Create a `.env` file in the root directory and add your Groq API key: `GROQ_API_KEY=your_key_here`
4. Run the app: `streamlit run app.py`

## 🧠 Key Learnings & Challenges
- **State Management:** Learned how to properly use `st.session_state` to prevent data loss during page reruns.
- **API Fallbacks:** Implemented a timeout and fallback mechanism when Gemini's free tier was hanging, switching to Groq for blazing-fast response times.
- **Data Sync:** Solved the challenge of syncing Pandas Dataframe edits back to the underlying Python dictionary state.