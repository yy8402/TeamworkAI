import openai
import json
import string
import random

# get api_url and api_key from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

openai.api_key = config['openai_api_key']
openai.api_base = config['openai_api_url']
llm_model = config['openai_api_model']

# load prompts from prompts.json
with open('prompt_templates.json', 'r') as file:
    prompt_templates = json.load(file)

# load json out examples from output_examples.json
with open('output_examples.json', 'r') as file:
    output_examples = json.load(file)

def api_request(prompt):
    response = openai.ChatCompletion.create(
        model=llm_model,
        messages=[
            {"role": "user", "content": prompt}
            ],
        max_tokens = 1000
    )
    return response["choices"][0]["message"]["content"]

def json_result(prompt, output_example):
    count = 0
    json_prompt = prompt + "\n\n please make sure the response is in json format, example output:\n" + output_example
    while True:
        result = api_request(json_prompt)
        try:
            result = json.loads(result)
            break
        except json.JSONDecodeError:
            count += 1
            if count == 5:
                print("Failed 5 times, break...")
                break
            else:
                print("Failed to parse the output to json format. Try again.")
    return result

def validate_prompt(prompt_template, values):
    formatter = string.Formatter()
    variables = [field_name for _, field_name, _, _ in formatter.parse(prompt_template) if field_name]
    
    unmatched_variables = []
    for variable in variables:
        if variable not in values:
            return unmatched_variables.append(variable)
    
    return unmatched_variables

def gen_prompt(request, variables):
    prompt_template = prompt_templates[request]
    prompt = prompt_template.format(**variables)

    unmatched_variables = validate_prompt(prompt_template, variables)
    if len(unmatched_variables) != 0:
        print("varabiles unfilled in {}: {}".format(request, unmatched_variables))

    return prompt

def define_personas(task_description):
    prompt_variables = {
        "task_description": task_description
    }
    prompt = gen_prompt("define_personas", prompt_variables)
    output_example = output_examples['define_personas']

    return json_result(prompt, output_example)

def define_workflow(task_description, personas):
    prompt_variables = {
        "personas": personas,
        "task_description": task_description
    }
    prompt = gen_prompt("define_workflow", prompt_variables)
    output_example = output_examples['define_workflow']
    return json_result(prompt, output_example)

def simulate_step(step_description, persona, output_from_last_step, expected_output, acceptance_criteria):
    prompt_variables = {
        "persona": persona,
        "step_description": step_description,
        "output_from_last_step": output_from_last_step,
        "expected_output": expected_output,
        "acceptance_criteria": acceptance_criteria
    }
    prompt = gen_prompt("simulate_step", prompt_variables)
    
    return api_request(prompt)

def grade_output(output, acceptance_criteria):
    prompt_variables = {
        "acceptance_criteria": acceptance_criteria,
        "output": output
    }
    prompt = gen_prompt("grade_output", prompt_variables)
    output_example = output_examples['grade_output']

    result_json = json_result(prompt, output_example)

    # result_grade = int(result_json['grade'])
    # grade_reasoning = result_json['reasoning']

    # print(f"Output: {output}")
    # print(f"Grade: {result_grade}")
    # print(f"Reasoning: {grade_reasoning}")

    return result_json