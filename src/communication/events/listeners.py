import time
import jwt
import json

from src.__init__ import socketio
from src.communication.events import emiters
from src.communication.agent_manager import AgentManager
from src.communication.events.prepare_action import handle_request
from src.manager import simulation_instance

agent_manager = AgentManager()
general_time = None
simulation_manager = None

agents = []
jobs = []
count = 1
jobs_done = []
aux = True


'''
    Receive all the jobs from the agents
    
    Instantiate the response considering that the result will be True
    Collect the JSON message and fit it on the agent variable
    If the handle_connection returns True
    Add the job to the jobs done list
    Emit response to the agent
    
    Else 
    Emit response containing False to the agents
'''


@socketio.on('receive_jobs')
def handle_connection(message):
    global count, jobs

    response = ['received_jobs_result', {'job_delivered': True}]

    message = json.loads(message)
    agent = (message['id'], (message['method'], message['parameters'][0], message['parameters'][1]))

    if handle_request(agent):
        jobs.append((count, (agent[1][0], agent[1][1], agent[1][2])))
        count += 1

    else:
        response[1]['job_delivered'] = False

    call_responses(response, 'receive_jobs')


'''
    Handle all the connections
    
    Instantiate the response considering that the result will be True
    Verify if the passed time get over the expected time 
    Verify if the number of agents connected get over the expected limit
    If passes the time limit 
        If passes the agents limit
            Add agent to the agents list and do a trick due to the implementation of flask
            The trick is that the method will not add the same agent twice because the method is called 
             twice by the flask module
        Else
            Reponse receive False
    Else
        Send to the agents the jobs that were finished
        Response receive False 
        
    Send to the agents the response from the method        
'''


@socketio.on('connect')
def respond_to_request(*message):
    global general_time, agents, aux

    response = ['connection_result', {'agent_connected': True}]

    if general_time is None:
        general_time = time.time()

    if time.time() - general_time < 5:
        if len(agents) > 5:
            response[1]['agent_connected'] = False

        else:
            if aux:
                agents.append('')
                aux = False

            else:
                aux = True

    else:
        jobs_done.append(simulation_instance.get_instance().do_step(jobs))
        call_responses(['jobs_result', jobs_done], 'results_from_actions')
        response[1]['agent_connected'] = False

    call_responses(response, 'connect')


'''
    Receive the agent information encoded and decode it
    Add the decoded agent to a list insed the agent_manager
    Use the singleton to get the simulation instance and prevent from instantiating the class multiple times
    Call two responsed:
        First containing the agents_list
        Second containg the simulation pre step
'''


@socketio.on('ready')
def respond_to_request_ready(message):
    global simulation_manager

    decoded = jwt.decode(message['data'], 'secret', algorithms=['HS256'])
    print('ready  :', decoded)

    agent_manager.manage_agents(decoded)

    simulation_manager = simulation_instance.get_instance()
    call_responses(simulation_manager.agents_list(), 'ready', message['data'])
    response = simulation_manager.do_pre_step()
    call_responses(response, message['data'])


'''
    Call the properly emiters from the 'emiters.py' file
'''


def call_responses(results, caller, *token):
    if caller == 'ready':
        emiters.response_to_action_ready(json.dumps(results), token)

    elif caller == 'connect':
        emiters.response_to_action_connect(results[0], results[1])

    elif caller == 'receive_jobs':
        emiters.response_to_action_deliver(results[0], results[1])

    elif caller == 'results_from_actions':
        emiters.response_jobs_result(results[0], results[1])

