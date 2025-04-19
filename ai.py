import random
import threading
from openai import OpenAI  # Synchronous client

client = OpenAI(api_key="sk-cb791902d7b04a28bd708ff5b2cc3805", base_url="https://api.deepseek.com")
response_queue = []
response_lock = threading.Lock()

def get_deepseek_response_async(prompt):
    def fetch_response():
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            with response_lock:
                response_queue.append(response.choices[0].message.content.strip())
        except Exception as e:
            with response_lock:
                response_queue.append(f"Error: {e}")
    
    threading.Thread(target=fetch_response, daemon=True).start()
    return "Processing..."

def suspect_ai(found_clues, suspect_visibility, language, points):
    if not found_clues:
        return suspect_visibility
    
    clue_count = len(found_clues)
    prompt = f"Generate a short alibi for a suspect in a theft case based on {clue_count} clues found. Language: {language}."
    if points > 20 and random.random() < 0.3:
        prompt += " Include a subtle red herring."
    
    response = get_deepseek_response_async(prompt)
    if response == "Processing...":
        with response_lock:
            if response_queue:
                alibi = response_queue.pop(0)
                print(f"AI Alibi: {alibi}")
                text_to_speech(alibi, language)
    
    for i in range(min(clue_count, len(suspect_visibility))):
        if not suspect_visibility[i]:
            suspect_visibility[i] = True
            break
    
    return suspect_visibility

def get_smart_hint(found_clues, points, language):
    clue_count = len(found_clues)
    difficulty = "easy" if points < 15 else "hard"
    prompt = f"Generate a short hint for a detective game with {clue_count} clues found so far. Difficulty: {difficulty}. Language: {language}."
    
    response = get_deepseek_response_async(prompt)
    if response == "Processing...":
        with response_lock:
            if response_queue:
                return response_queue.pop(0)
    return response