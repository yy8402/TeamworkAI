import json
from datetime import datetime 
from openai import OpenAI


# get api_url and api_key from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

openai_client = OpenAI(
    api_key=config['openai']['api_key'],
    base_url=config['openai']['api_url']  
)
openai_model = config['openai']['api_model']

LOG_LLM_PROMPT = config['logging']['llm_prompt']
LOG_LLM_RESPONSE = config['logging']['llm_response']

def log_llm(message, type="prompt"):
    if not LOG_LLM_PROMPT and not LOG_LLM_RESPONSE:
        return True
    
    with open('logs/openai.log', 'a') as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} {type}: {message}"
        file.write(log_message + "\n")

    return True

def create_chat(prompt, model = openai_model):
    prompt_messages = [
        {"role": "user", "content": prompt}
    ]
    log_llm(json.dumps(prompt_messages))

    response = openai_client.chat.completions.create(
        messages=prompt_messages,
        model=model,
    )
    log_llm(f"Reason:{response.choices[0].finish_reason}; Content: {response.choices[0].message.content}", type="response")

    return response

def api_request(prompt,  model = openai_model):
    result_content = ""
    response_content = create_chat(prompt, model)
    result_content += response_content.choices[0].message.content
    while True:
        if response_content.choices[0].finish_reason == "length":
            response = create_chat(response_content.choices[0].message.content, model)

            # append the new response to the previous response
            result_content += response["choices"][0]["message"]["content"]
        else:
            break

    return result_content
    # result = {} 
    # result["text"] = response_content
    # result["reason"] = response["choices"][0]["finish_reason"]
    # return result