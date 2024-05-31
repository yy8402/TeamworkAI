from flask import Flask, render_template, request, session, redirect
import teamwork
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(filename='logs/service.log', level=logging.INFO)

def handle_task():
    task = request.form.get('task')
    if task is None:
        return redirect('/')
    
    session['task'] = task
    personas = teamwork.define_personas(task)
    session['personas'] = personas
    return render_template('step2.html', personas=personas)

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
        session.clear()  # Clear session data
        return render_template('step1.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
        