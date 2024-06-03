# import google.generativeai as genai

# # Set the API key
# gemini_api_key = "MY-GEMINI-TOKEN"

# genai.configure(api_key=gemini_api_key)
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("Write a story about a magic backpack.")
# print(response.text)

import requests
import json
from datetime import datetime

with open('config.json', 'r') as file:
    config = json.load(file)

BASE_URL = config['gemini']['api_url']
API_KEY = config['gemini']['api_key']
GEMINI_MODEL = config['gemini']['api_model']

LOG_LLM_PROMPT = config['logging']['llm_prompt']
LOG_LLM_RESPONSE = config['logging']['llm_response']

def log_llm(message, type="prompt"):
    if not LOG_LLM_PROMPT and not LOG_LLM_RESPONSE:
        return True
    
    with open('logs/gemini.log', 'a') as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} {type}: {message}"
        file.write(log_message + "\n")
        
    return True

def generate_content(prompt, model = GEMINI_MODEL):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    api_url = f"{BASE_URL}/v1beta/models/{model}:generateContent?key={API_KEY}"
    log_llm(json.dumps(data))

    response = requests.post(api_url, headers=headers, json=data)
    # dump the raw content of response to log file
    log_llm(f"json.dumps(response.json)", type="response")

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    else:
        return response.json()


def api_request(prompt, model = GEMINI_MODEL):
    response_json = generate_content(prompt, model)
    if response_json is None:
        return None
    else:
        return response_json['candidates'][0]['content']['parts'][0]['text']
    # result = {}
    # result["text"] = response_json['candidates'][0]['content']['parts'][0]['text']
    # result["reason"] = response_json['candidates'][0]['finishReason'] 
    # # "FINISH_REASON_UNSPECIFIED", "STOP", "MAX_TOKENS", "SAFETY", "RECITATION", "OTHER"

    # return result

# response = api_request("Write a story about a magic backpack.")