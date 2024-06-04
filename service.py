from flask import Flask, render_template, request, session, redirect
import teamwork
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(filename='logs/service.log', level=logging.INFO)
teamwork.validate_examples()

def handle_task():
    task = request.form.get('task')
    if task is None:
        return redirect('/')
    
    session['task'] = task
    personas = teamwork.define_personas(task)
    session['personas'] = personas
    return render_template('step2.html', personas=personas)

def delete_persona(persona_name):
    personas = session['personas']
    for persona in personas:
        if persona['name'] == persona_name:
            personas.remove(persona)
            session['personas'] = personas
            break
    return True

def update_persona(persona_name,  persona_description , skills, persona_role):
    personas = session['personas']
    persona_exists = False
    for persona in personas:
        if persona['name'] == persona_name:
            persona_exists = True
            persona['description'] = persona_description
            persona['skills'] = skills
            persona['role'] = persona_role
            session['personas'] = personas
            break

    if not persona_exists:
        new_persona = {
            'name': persona_name,
            'description': persona_description,
            'skills': skills,
            'role': persona_role
        }
        personas.append(new_persona)

    return True

def handle_personas():
    task = session['task']
    personas = session['personas'] 
    workflow = teamwork.define_workflow(task, personas)
    # TODO: validate workflow
    # for step in workflow:
    #     if step['persona'] not in personas:
    #         logging.error("Persona not found in session")

    session['workflow'] = workflow
    return render_template('step3.html', workflow=workflow)

def init_workflow():
    session['outputs'] = []
    session['grades'] = [] 
    session['current_step'] = 0

def delete_step(step_index):
    workflow = session['workflow']
    workflow.pop(step_index)
    session['workflow'] = workflow
    return True

def update_step(step_index, step_description, expected_output, acceptance_criteria, assignee):
    workflow = session['workflow']
    step = {
        'description': step_description,
        'expected_output': expected_output,
        'acceptance_criteria': acceptance_criteria,
        'assignee': assignee
    }
    workflow[step_index] = step
    session['workflow'] = workflow
    return True

def add_step(step_index, step_description, expected_output, acceptance_criteria, assignee):
    workflow = session['workflow']
    step = {
        'description': step_description,
        'expected_output': expected_output,
        'acceptance_criteria': acceptance_criteria,
        'assignee': assignee
    }
    workflow.insert(step_index, step)

    outputs = session['outputs']
    grades = session['grades']
    outputs.insert(step_index, None)
    grades.insert(step_index, None)

    session['workflow'] = workflow
    session['outputs'] = outputs
    session['grades'] = grades
    return True

def handle_workflow():
    workflow = session['workflow']
    if 'current_step' not in session:
        init_workflow()
    elif session['current_step'] == len(workflow):
        return render_final_result()
    else:
        step_last_output = session['outputs'][-1]

    this_step = workflow[session['current_step']]
    step_count = session['current_step'] + 1
    step_output, step_grade = simulate_step(this_step, step_last_output)
    session['current_step'] += 1
    return render_template('outputs.html', 
                           current_step=step_count, 
                           total_steps=len(workflow), 
                           step_description=this_step['description'], 
                           result=step_output, 
                           grade_num=step_grade['grade'], 
                           grade_reasoning=step_grade['reasoning'])

def simulate_step(step, last_output):
    step_description = step['description']    
    expected_output = step['expected_output']
    acceptance_criteria = step['acceptance_criteria']

    assignee_name = step['assignee']
    assignee_role = None
    assignee_description = None
    for persona in session['personas']:
        if persona['name'] == assignee_name:
            assignee_role = persona['role']
            assignee_description = persona['description']
            break
    if assignee_role is None:
        raise ValueError("Persona not found in session")
    
    output = teamwork.simulate_step(
        step_description,
        assignee_name,
        assignee_role,
        assignee_description,
        last_output,
        expected_output,
        acceptance_criteria
    )
    
    grade = teamwork.grade_output(output, acceptance_criteria)

    session['outputs'].append(output)
    session['grades'].append(grade)
    return output, grade

def render_final_result():
    result = session['outputs'][-1]
    grade = session['grades'][-1]
    return render_template('result.html', result=result, grade=grade)

@app.route('/', methods=['GET', 'POST'])
def service():
    if request.method == 'POST':
        if 'personas' not in session:
            return handle_task()
        elif 'workflow' not in session:
            form_personas = request.form.getlist('personas')
            if form_personas:
                session['personas'] = form_personas
            return handle_personas()
        elif 'result' not in session:
            form_workflow = request.form.getlist('workflow')
            if form_workflow:
                session['workflow'] = form_workflow
            return handle_workflow()
        else:
            return redirect('/')
    else:
        return render_template('step2.html')


@app.route('/delete_persona', methods=['POST'])
def delete_persona_route():
    persona_name = request.form.get('persona_name')
    delete_persona(persona_name)
    return redirect('/')

@app.route('/update_persona', methods=['POST'])
def update_persona_route():
    persona_name = request.form.get('persona_name')
    persona_description = request.form.get('persona_description')
    skills = request.form.get('skills')
    persona_role = request.form.get('persona_role')
    update_persona(persona_name, persona_description, skills, persona_role)
    return redirect('/')

@app.route('/delete_step', methods=['POST'])
def delete_step_route():
    step_index = int(request.form.get('step_index'))
    delete_step(step_index)
    return redirect('/')

@app.route('/update_step', methods=['POST'])
def update_step_route():
    step_index = int(request.form.get('step_index'))
    step_description = request.form.get('step_description')
    expected_output = request.form.get('expected_output')
    acceptance_criteria = request.form.get('acceptance_criteria')
    assignee = request.form.get('assignee')
    update_step(step_index, step_description, expected_output, acceptance_criteria, assignee)
    return redirect('/')

@app.route('/add_step', methods=['POST'])
def add_step_route():
    step_index = int(request.form.get('step_index'))
    step_description = request.form.get('step_description')
    expected_output = request.form.get('expected_output')
    acceptance_criteria = request.form.get('acceptance_criteria')
    assignee = request.form.get('assignee')
    add_step(step_index, step_description, expected_output, acceptance_criteria, assignee)
    return redirect('/')

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return redirect('/')

@app.route('/step1', methods=['GET'])
def step1():
    return render_template('step1.html')

@app.route('/step2', methods=['GET'])
def step2():
    return render_template('step2.html')

@app.route('/step3', methods=['GET'])
def step3():
    workflow = session['workflow']
    return render_template('step3.html', workflow=workflow)

@app.route('/outputs', methods=['GET'])
def outputs():
    step_count = session['current_step']
    workflow = session['workflow']
    this_step = workflow[step_count]
    step_output = outputs[step_count]
    grades = session['grades']
    step_grade = grades[step_count]
    return render_template('outputs.html', 
                           current_step=step_count, 
                           total_steps=len(workflow), 
                           step_description=this_step['description'], 
                           result=step_output, 
                           grade_num=step_grade['grade'], 
                           grade_reasoning=step_grade['reasoning'])

@app.route('/result', methods=['GET'])
def result():
    return render_final_result

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
        