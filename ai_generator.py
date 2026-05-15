import google.generativeai as genai
import json
import os
from dotenv import load_dotenv # Add this

load_dotenv() # Add this: It loads the variables from your .env file
# 1. Load API key securely from environment variables
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=api_key)

# 2. Initialize the model 
model = genai.GenerativeModel("gemini-2.5-flash") # Updated to standard flash model name
import random
import requests
OFFLINE_PRODUCTIVITY_TIPS = [
    "Break large tasks into smaller subtasks.",
    "Use Pomodoro sessions for difficult work.",
    "Complete high-priority tasks first.",
    "Avoid multitasking during focus sessions.",
    "Take short breaks to maintain concentration.",
    "Finish pending tasks before starting new ones.",
    "Schedule difficult tasks during peak productivity hours.",
    "Review your goals every morning."
]
def is_online():
    try:
        requests.get(
            "https://google.com",
            timeout=3
        )
        return True
    except:
        return False
def generate_question(topic, difficulty):
    prompt = f"""
    Generate ONE competitive exam level aptitude or reasoning question.

    The question should be similar to exams like GATE General Aptitude, CAT, or placement tests.

    Topic: {topic}
    Difficulty: {difficulty}

    IMPORTANT:
    - Do NOT generate technical or engineering subject questions
    - Only aptitude, reasoning, or numerical ability

    Format STRICTLY in JSON:

    {{
        "question": "question text",
        "options": ["A", "B", "C", "D"],
        "answer": "correct option",
        "explanation": "short explanation"
    }}
    """

    try:
        # 3. Force JSON output via generation_config
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        # Now it is safe to load directly, as the API guarantees clean JSON
        data = json.loads(response.text)
        return data

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return None
def generate_motivation(user_problem):
    if not is_online():
        return random.choice(
            OFFLINE_PRODUCTIVITY_TIPS
        )
    import google.generativeai as genai
    import streamlit as st

    genai.configure(api_key=api_key)

# 2. Initialize the model 
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    The user is struggling with productivity.

    Problem: {user_problem}

    Provide a short, motivating, and practical response to help the user improve.

    Keep it simple, encouraging, and actionable.
    """

    response = model.generate_content(prompt)

    return response.text
# Example Usage:
if __name__ == "__main__":
    mcq = generate_question("Time and Work", "Hard")
    if mcq:
        print(json.dumps(mcq, indent=2))

def generate_task_suggestions(task_list):
    if not is_online():
        return (
            "📴 Offline Mode\n\n"
            + random.choice(OFFLINE_PRODUCTIVITY_TIPS)
        )
    prompt = f"""
    You are a smart productivity assistant.
    Analyze these tasks and give practical productivity advice.
    Tasks:
    {task_list}
    Suggest:
    - which task to prioritize
    - workload analysis
    - productivity tips
    - recommended order
    - focus suggestions
    Keep response short and practical.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"