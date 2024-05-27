import openai
import json

# get api_url and api_key from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

openai.api_key = config['openai']['api_key']
openai.api_base = config['openai']['api_url']
openai_model = config['openai']['api_model']


def create_chat(prompt, model = openai_model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
            ],
        max_tokens = 1000
    )

    return response

def api_request(prompt,  model = openai_model):
    result_content = ""
    response_content = create_chat(prompt, model)
    result_content += response_content["choices"][0]["message"]["content"]
    while True:
        if response_content["choices"][0]["finish_reason"] == "length":
            response = create_chat(response_content["choices"][0]["message"]["content"], model)

            # append the new response to the previous response
            result_content += response["choices"][0]["message"]["content"]
        else:
            break

    return result_content
    # result = {} 
    # result["text"] = response_content
    # result["reason"] = response["choices"][0]["finish_reason"]
    # return result