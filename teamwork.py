import json
import string
import random

import openai_api
import gemini_api


# load prompts from prompts.json
with open('prompt_templates.json', 'r') as file:
    prompt_templates = json.load(file)

# load json out examples from output_examples.json
with open('output_examples.json', 'r') as file:
    output_examples = json.load(file)

def api_request(prompt, llm_mode = "gpt-3.5-turbo"):
    if llm_mode == "gpt-3.5-turbo":
        return openai_api.api_request(prompt, llm_mode)
    elif llm_mode == "gemini-pro":
        return gemini_api.api_request(prompt, llm_mode)
    else:
        print ("ERROR: %s is not supported", llm_mode)
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

def prompt_user_for_task():
    return input("Please describe the task you want to accomplish: ")


def edit_persona(persona):
    persona_name = persona["name"]
    new_description = input("Please provide the updated description: ") or persona["description"]
    new_skills = input("Please provide the updated skills (comma-separated): ").split(",") or persona["skills"]
    new_role = input("Please provide the updated role: ") or persona["role"]
    new_persona = {
        "name": persona_name,
        "description": new_description,
        "skills": new_skills,
        "role": new_role
    }
    return new_persona

def persona_changes(personas):
    print("Please add or delete or edit a persona.")
    print("Current Personas:")

    while True:
        for index, persona in enumerate(personas):
            print(f"{index+1}. {persona}")
    
        action = input("Do you want to add or delete or edit a persona? (add/delete/edit/no): ")
        if action == "add":
            new_persona = {}
            new_persona["name"] = input("Please provide the name of the new persona: ") or "DefaultName".join(random.choices(string.digits, k=6))
            personas.append(new_persona)
        elif action == "delete":
            delete_index = int(input("Please provide the index of the persona to delete: "))
            if delete_index >= 1 and delete_index <= len(personas):
                personas.pop(delete_index - 1)
            else:
                print("Invalid index. Please provide a valid index.")
        elif action == "edit":
            edit_index = int(input("Please provide the index of the persona to edit: "))
            if edit_index >= 1 and edit_index <= len(personas):
                persona = personas[edit_index - 1]
                personas[edit_index - 1] = edit_persona(persona)
            else:
                print("Invalid index. Please provide a valid index.")
        elif action == "no":
            break

    return personas

def update_step(step):
    print ("Current Step:")
    print (f"\tDescription: {step['description']}\n\tPersona: {step['persona']}\n\tExpected Output: {step['expected_output']}\n\tAcceptance Criteria: {step['acceptance_criteria']}")

    updated_step = {}
    updated_step["description"] = input("Please provide the updated description: ") or step["description"]
    updated_step["persona"] = input("Please provide the updated persona: ") or step["persona"]
    updated_step["expected_output"] = input("Please provide the updated expected output: ") or step["expected_output"]
    updated_step["acceptance_criteria"] = input("Please provide the updated acceptance criteria: ") or step["acceptance_criteria"]
    return updated_step

def workflow_changes(workflow_steps):
    print("Please add or delete a workflow step.")
    print("Current Workflow Steps:")

    while True:
        for index, step in enumerate(workflow_steps):
            print(f"{index+1}. {step}")
        
        action = input("Do you want to add or delete a workflow step? (add/delete/update/no): ")
        if action == "add":
            index = int(input("Please provide the index where you want to add the new workflow step: "))
            new_step = {}
            new_step = update_step(new_step)
            if index >= 1 and index <= len(workflow_steps) + 1:
                workflow_steps.insert(index - 1, new_step)
            else:
                print("Invalid index. Please provide a valid index.")
        elif action == "delete":
            delete_index = int(input("Please provide the index of the workflow step to delete: "))
            if delete_index >= 1 and delete_index <= len(workflow_steps):
                workflow_steps.pop(delete_index - 1)
            else:
                print("Invalid index. Please provide a valid index.")
        elif action == "update":
            update_index = int(input("Please provide the index of the workflow step to update: "))
            if update_index >= 1 and update_index <= len(workflow_steps):
                step = workflow_steps[update_index - 1]
                updated_step = update_step(step)
                workflow_steps[update_index - 1] = updated_step
            else:
                print("Invalid index. Please provide a valid index.")
        elif action == "no":
            break
        else:
            print("Invalid input. Please input 'add', 'delete', 'update' or 'no'.")

    return workflow_steps
