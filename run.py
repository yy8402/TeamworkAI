import teamwork

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

def main():
    task = prompt_user_for_task()
    personas = teamwork.define_personas(task)

    # ask the user to confirm the personas and add/remove personas if needed
    while True:
        # print persons with index
        print("Current Personas:")
        for index, persona in enumerate(personas):
            print(f"{index+1}. {persona['name']} {persona['description']}")
        confirmation = input("Do you want to make changes to the personas? (yes/no): ")
        if confirmation == "no":
            break
        elif confirmation == "yes":
            personas = persona_changes(personas)
            break
        else:
            print("Invalid input. Please input 'yes' or 'no'.")
    
    workflow_steps = teamwork.define_workflow(task, personas)

    # ask the user to confirm the workflow steps and add/remove steps if needed
    while True:
        # print steps with index
        print("Current Workflow Steps:")
        for index, step in enumerate(workflow_steps):
            print(f"{index+1}. {step['description']}")

        confirmation = input("Do you want to make changes to the workflow steps? (yes/no): ")
        if confirmation == "no":
            break
        elif confirmation == "yes":
            workflow_steps = workflow_changes(workflow_steps)
            break
        else:
            print("Invalid input. Please input 'yes' or 'no'.")

    output_from_last_step = None
    output_result = []
    for step in workflow_steps:
        while True:
            output = teamwork.simulate_step(step['description'], 
                                            step['persona'], 
                                            output_from_last_step, 
                                            step['expected_output'], 
                                            step['acceptance_criteria'])
            grade = teamwork.grade_output(output, step['acceptance_criteria'])
            
            if grade['grade'] >= 80:
                break
            else:
                print(f"Repeating step due to low grade ({grade['grade']}): step['description']")
        
        output_from_last_step = output
        output_result.append(output)
    
    print("Final Result:")
    print(output_result)

if __name__ == "__main__":
    main()