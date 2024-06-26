import json
import string
import logging

import openai_api
import gemini_api

# load prompts from prompts.json
with open('prompt_templates.json', 'r') as file:
    prompt_templates = json.load(file)

# load json out examples from output_examples.json
with open('output_examples.json', 'r') as file:
    output_examples = json.load(file)

def validate_persona(persona):
    if 'name' not in persona:
        logging.error(f"name not in persona, persona: {persona}")
        return False
    if 'role' not in persona:
        logging.error(f"role not in persona, persona: {persona}")
        return False
    if 'description' not in persona:
        logging.error(f"description not in persona, persona: {persona}")
        return False
    if 'skills' not in persona:
        logging.error(f"skills not in persona, persona: {persona}")
        return False

    return True

def validate_step(step):
    if 'description' not in step:
        logging.error(f"description not in step, step: {step}")
        return False
    if 'assignee' not in step:
        logging.error(f"assignee not in step, step: {step}")
        return False
    if 'expected_output' not in step:
        logging.error(f"expected_output not in step, step: {step}")
        return False
    if 'acceptance_criteria' not in step:
        logging.error(f"acceptance_criteria not in step, step: {step}")
        return False

    return True

def validate_examples():
    # persona keys: name, role, description, skills
    personas_example = output_examples['define_personas']
    for persona in personas_example:
        if not validate_persona(persona):
            return False
    # workflow/step keys: description, assignee, expected_output, acceptance_criteria
    workflow_example = output_examples['define_workflow']
    for step in workflow_example:
        if not validate_step(step):
            return False
    # grade keys: grade, reasoning

    return True

def api_request(prompt, llm_mode = "gpt-3.5-turbo"):
    if llm_mode == "gpt-3.5-turbo":
        logging.debug(f"Prompt: \n\n {prompt}\n")
        return openai_api.api_request(prompt, llm_mode)
    elif llm_mode == "gemini-pro":
        return gemini_api.api_request(prompt, llm_mode)
    else:
        logging.error(f"ERROR: {llm_mode} is not supported")
        return None

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
                logging.error("Failed 5 times, break...")
                break
            else:
                logging.info("Failed to parse the output to json format. Try again.")
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
        logging.error("varabiles unfilled in {}: {}".format(request, unmatched_variables))

    return prompt

def define_personas(task_description):
    prompt_variables = {
        "task_description": task_description
    }
    prompt = gen_prompt("define_personas", prompt_variables)
    output_example = output_examples['define_personas']

    return json_result(prompt, output_example)

def define_workflow(task_description, personas):
    persona_info = ""
    for persona in personas:
        persona_info += f"{persona['name']}, {persona['role']}; "
    prompt_variables = {
        "persona_info": persona_info,
        "task_description": task_description
    }
    prompt = gen_prompt("define_workflow", prompt_variables)
    output_example = output_examples['define_workflow']
    return json_result(prompt, output_example)

def simulate_step(step_description, 
                  assignee_name, 
                  assignee_role, 
                  assignee_description, 
                  step_input, 
                  expected_output, 
                  acceptance_criteria):
    prompt_variables = {
        "assignee_name": assignee_name,
        "assignee_role": assignee_role,
        "assignee_description": assignee_description,
        "step_description": step_description,
        "step_input": step_input,
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

    # logging.debug(f"Output: {output}")
    # logging.debug(f"Grade: {result_grade}")
    # logging.debug(f"Reasoning: {grade_reasoning}")

    return result_json
