# import google.generativeai as genai

# # Set the API key
# gemini_api_key = "MY-GEMINI-TOKEN"

# genai.configure(api_key=gemini_api_key)
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content("Write a story about a magic backpack.")
# print(response.text)

import requests
import json

with open('config.json', 'r') as file:
    config = json.load(file)

BASE_URL = config['gemini']['api_url']
API_KEY = config['gemini']['api_key']
GEMINI_MODEL = config['gemini']['api_model']

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
    print (api_url)
    response = requests.post(api_url, headers=headers, json=data)

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