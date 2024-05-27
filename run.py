import teamwork

def main():
    task = teamwork.prompt_user_for_task()
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
            personas = teamwork.persona_changes(personas)
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
            workflow_steps = teamwork.workflow_changes(workflow_steps)
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