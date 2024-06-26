from flask import Flask, render_template, request, session, redirect
import logging
import psycopg2
import json

import teamwork
import tasksession

app = Flask(__name__)
app.secret_key = tasksession.random_string(24)
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

def create_db():
    with open('config.json') as f:
        config = json.load(f)
    db_config = config['postgresql']
    db_host = db_config['dbhost']
    db_password = db_config['password']
    db_name = db_config['dbname']

    # Connect to the default PostgreSQL database as the superuser 'postgres'
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password=db_password,
        host=db_host
    )

    conn.autocommit = True
    cursor = conn.cursor()

    # Check if the database 'db_name' exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    exists = cursor.fetchone()

    # If the database does not exist, create it
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name};")

    # Close the cursor and connection to the default database
    cursor.close()
    conn.close()

    # Connect to the database
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['dbhost']
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Create the 'sessions' table
    cur.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, session_info TEXT);")

    # Close the cursor and connection to the database
    cur.close()
    conn.close()

def get_db_conn():
    with open('config.json') as f:
        config = json.load(f)
    db_config = config['postgresql']

    # Connect to the database
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['dbhost']
    )
    cur = conn.cursor()

    return conn, cur


def db_get_session_by_id(session_id):
    conn, cur = get_db_conn()
    cur.execute("SELECT session_info FROM sessions WHERE session_id = %s", (session_id,))
    session_info = cur.fetchone()
    if session_info is None:
        logging.error(f"Session not found in database: {session_id}")
        return None
    logging.debug(f"Retrieved session from database: {session_info}")
    cur.close()
    conn.close()
    return json.loads(session_info[0])

def db_update_session(working_session):
    logging.debug(f"Updating session in database: {working_session}")
    try:
        conn, cur = get_db_conn()
        cur.execute("UPDATE sessions SET session_info = %s WHERE session_id = %s", (json.dumps(working_session), working_session['id']))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO sessions (session_id, session_info) VALUES (%s, %s)", (working_session['id'], json.dumps(working_session)))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error updating session in database: {str(e)}")
        return False

def render_final_result(working_session):
    result = working_session['workflow'][-1]['output']
    grade = working_session['workflow'][-1]['grades']
    return render_template('result.html', result=result, grade=grade)

def grade_step(step):
    #TODO: validate grade result
    return teamwork.grade_output(step['output'], step['acceptance_criteria'])

def simulate_step(personas, step):
    step_description = step['description']    
    expected_output = step['expected_output_example']
    # expected_output_description = step['expected_output_description']
    acceptance_criteria = step['acceptance_criteria']

    assignee_name = step['assignee']
    assignee_role = None
    assignee_description = None
    for persona in personas:
        if persona['name'] == assignee_name:
            assignee_role = persona['role']
            assignee_description = persona['description']
            break
    if assignee_role is None:
        raise ValueError("Persona not found in session")
    
    step['output'] = teamwork.simulate_step(
        step_description,
        assignee_name,
        assignee_role,
        assignee_description,
        step['input'],
        expected_output,
        acceptance_criteria
    )
    
    step['grade'] = grade_step(step)
    return step

def get_step_index(current_step, retry):
    if retry:
        return current_step - 1
    else:
        return current_step

def handle_workflow(working_session):
    workflow = working_session.get('workflow')
    current_step = working_session.get('current_step')
    if not current_step:
        working_session['current_step'] = 0
        current_step = 0
        output_last_step = None
    elif current_step == 0:
        output_last_step = None
    elif current_step == len(workflow) - 1 :
        return render_final_result(working_session)
    else:
        output_last_step = workflow[current_step - 1]['output']  

    logging.debug(f"Handling workflow step: {current_step}, workflow: {workflow}, session: {working_session}")

    this_step = workflow[current_step]
    this_step['input'] = output_last_step
    this_step = simulate_step(working_session['personas'], this_step)
    logging.debug(f"Simulated step: {this_step}")

    # update session with update step including output and grade
    #TODO: validate step_output and step_grade
    workflow[current_step] = this_step
    working_session['workflow'] = workflow
    step_count = current_step + 1
    working_session['current_step'] = step_count

    if db_update_session(working_session):
        logging.info(f"Session updated with step {step_count}")
    else:
        logging.error(f"Error updating session with step {step_count}")

    return render_template('outputs.html', 
                           step_count=step_count,
                           total_steps=len(workflow), 
                           step=this_step)

def get_session_info():
    if 'id' not in session:
        working_session = tasksession.init_session()
        session['id'] = working_session['id']
    else:
        session_id = session['id']
        working_session = db_get_session_by_id(session_id)
        if working_session is None:
            working_session = tasksession.init_session()
            session['id'] = working_session['id']
        
    logging.debug(f"Get session info: {working_session}")
    return working_session

def update_session(working_session, request_form):
    # validate working_session
    if working_session is None:
        logging.error("Session not found")
        return 'session not found', 404
    
    if 'task' in request_form:
        result_update = tasksession.set_task(working_session, 
                                             request_form.get('task'))
    elif 'personas' in request_form:
        result_update = tasksession.set_personas(working_session, 
                                                 request_form.get('personas'))
    elif 'workflow' in request_form:
        result_update = tasksession.set_workflow(working_session, 
                                                 request_form.get('workflow'))
    elif 'new_persona' in request_form:
        result_update = tasksession.add_persona(working_session, 
                                                request_form.get('new_persona'))
    elif 'new_step' in request_form:
        result_update = tasksession.add_step(working_session, 
                                             request_form.get('new_step'), 
                                             request_form.get('step_info'))
    elif 'delete_persona' in request_form:
        result_update = tasksession.delete_persona(working_session, 
                                                   request_form.get('delete_persona'))
    elif 'delete_step' in request_form:
        result_update = tasksession.delete_step(working_session, 
                                                request_form.get('delete_step'))
    elif 'update_persona' in request_form:
        result_update = tasksession.update_persona(working_session, 
                                                   request_form.get('update_persona'), 
                                                   request_form.get('persona_info'))
    elif 'update_step' in request_form:
        step_index = request_form.get('step_count') - 1
        step_info = working_session['workflow'][step_index]
        step_info['description'] = request_form.get('step_description')
        step_info['expected_output_description'] = request_form.get('step_expected_output_description')
        step_info['expected_output_example'] = request_form.get('step_expected_output_example')
        step_info['acceptance_criteria'] = request_form.get('step_acceptance_criteria')
        result_update = tasksession.update_step(working_session, 
                                                step_index=step_index, 
                                                step_info=step_info)
        if result_update['status'] == 'success':
            working_session = result_update['session']
    elif 'regrade' in request_form:
        step_index = request_form.get('step_count') - 1
        new_grade = grade_step(working_session['workflow'][step_index])
        result_update = tasksession.update_step_grade(working_session, 
                                                      step_index, 
                                                      new_grade)
    else:
        logging.debug("No update action specified")
        return working_session
    
    return_status = result_update['status']
    return_message = result_update['message']
    working_session = result_update['session']
    if return_status != 'success':
        logging.error(f"Error updating session: {return_message}")
        return return_message, 400

    if db_update_session(working_session):
        logging.info(f"Session updated")
        return working_session
    else:
        logging.error(f"Error updating session")
        return 'error updating session', 500

def move_to_next_stage(working_session, request_form):
    working_session = update_session(working_session, request_form)

    if working_session['task'] == '':
        logging.debug(f"Task not defined in session: {working_session}")
        return render_template('task.html', task='')
    elif working_session['personas'] == []:
        personas = teamwork.define_personas(working_session['task'])
        # TODO: handle error
        # TODO: validate personas
        result_update = tasksession.set_personas(working_session, 
                                                 personas)
        return_status = result_update['status']
        return_message = result_update['message']
        working_session = result_update['session']
        if return_status == 'success' and db_update_session(working_session):
            logging.info(f"Personas defined: {personas}")
            return render_template('personas.html', personas=personas)
        else:
            logging.error(f"Error defining personas: {return_message}")
            return render_template('task.html', task=working_session['task'])
    elif working_session['workflow'] == []:
        workflow = teamwork.define_workflow(working_session['task'], working_session['personas'])
        #TODO: handle error
        #TODO: validate workflow
        result_update = tasksession.set_workflow(working_session, 
                                                 workflow)
        return_status = result_update['status']
        return_message = result_update['message']
        working_session = result_update['session']
        if return_status == 'success' and db_update_session(working_session):
            logging.info(f"Workflow defined: {workflow}")
            return render_template('workflow.html', workflow=workflow)
        else:
            logging.error(f"Error defining workflow: {return_message}")
            return render_template('personas.html', personas=working_session['personas'])
    else:
        logging.debug(f"Session is ready for workflow: {working_session}")
        return handle_workflow(working_session)

def handle_update(working_session, request_form):
    action = request_form.get('action')
    if action == 'next_stage':
        return move_to_next_stage(working_session, request_form)
    elif action == 'next_step': 
        return handle_workflow(working_session)
    elif action == 'retry_step' or action == 'regrade':
        working_session['current_step'] = working_session['current_step'] -1   
        return handle_workflow(working_session)
    elif action == 'update':
        working_session = update_session(working_session, request_form)
        return 'session updated', 200
    else:
        return 'invalid action', 400
    
def present_info():
    working_session = get_session_info()
    return render_template('present.html', working_session=working_session)

@app.route('/', methods=['GET', 'POST'])
def service():
    working_session = get_session_info()

    # get session id from URL parameter
    session_id = request.args.get('id')
    if session_id:
        working_session = db_get_session_by_id(session_id)

    if request.method == 'POST':
        request_form = request.form
        return handle_update(working_session, request_form)
    else:
        if working_session.get('task') == '':
            return render_template('task.html', task='')
        elif working_session.get('personas') == []:
            return render_template('task.html', task=working_session.get('task'))
        elif working_session.get('workflow') == []:
            return render_template('personas.html', personas=working_session.get('personas'))
        else:
            return render_template('workflow.html', workflow=working_session.get('workflow'))

@app.route('/info', methods=['GET'])
def info():
    # get session id from URL parameter
    session_id = request.args.get('id')
    if session_id:
        session['id'] = session_id
        return present_info()
    elif 'id' in session:
        return present_info()
    else:
        return 'no info', 200

@app.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    create_db()
    app.run(debug=True, host='0.0.0.0')