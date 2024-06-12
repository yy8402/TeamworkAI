import random
import string
import time

def random_string(length):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def init_session():
    working_session = dict()
    working_session['id'] = random_string(24)
    working_session['create_time'] = int(time.time())
    working_session['task'] = ''
    working_session['personas'] = []
    working_session['workflow'] = []
    working_session['outputs'] = []
    working_session['results'] = []
    working_session['grades'] = []
    return working_session

def set_task(working_session, task):
    return_status = 'success'
    return_message = 'task set'

    working_session['task'] = task
    working_session['personas'] = []
    working_session['workflow'] = []
    working_session['outputs'] = []
    working_session['grades'] = []
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def set_personas(working_session, personas):
    return_status = 'success'
    return_message = 'personas set'

    #TODO: validate personas
    working_session['personas'] = personas
    working_session['workflow'] = []
    working_session['outputs'] = []
    working_session['grades'] = []
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def set_workflow(working_session, workflow):
    return_status = 'success'
    return_message = 'workflow set'

    #TODO: validate workflow
    working_session['workflow'] = workflow
    working_session['outputs'] = []
    working_session['grades'] = []
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def add_persona(working_session, new_persona):
    return_status = 'success'
    return_message = 'persona added'

    # TODO: validate new_persona
    working_session['personas'].append(new_persona)
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def add_step(working_session, step_index, step_info):
    return_status = 'success'
    return_message = 'step added'

    workflow = working_session['workflow']
    # TODO: validate step_info
    workflow.insert(step_index, step_info)
    working_session['workflow'] = workflow
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def delete_persona(working_session, persona_name):
    return_status = 'failed'
    return_message = 'persona not found'

    personas = working_session['personas']
    for persona in personas:
        if persona['name'] == persona_name:
            personas.remove(persona)
            working_session['personas'] = personas

            return_status = 'success'
            return_message = 'step deleted'
            break
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def delete_step(working_session, step_index):
    return_status = 'failed'
    return_message = 'step not found'

    workflow = working_session['workflow']
    if step_index < len(workflow):
        workflow.pop(step_index)
        working_session['workflow'] = workflow
        return_status = 'success'
        return_message = 'step deleted'

    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def update_persona(working_session, persona_name, persona_info):
    return_status = 'failed'
    return_message = 'persona not found'

    if persona_name != persona_info['name']:
        return 'name mismatch', 400
    #TODO: validate persona_info
    for persona in working_session['personas']:
        if persona['name'] == persona_name:
            persona = persona_info
            return_status = 'success'
            return_message = 'persona updated'
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }

def update_step(working_session, step_index, step_info):
    return_status = 'failed'
    return_message = 'step not found'

    workflow = working_session['workflow']
    if step_index < len(workflow):
        #TODO: validate step_info
        workflow[step_index] = step_info
        working_session['workflow'] = workflow
        return_status = 'success'
        return_message = 'step updated'
    return {
        "status": return_status, 
        "message": return_message,
        "session": working_session
        }