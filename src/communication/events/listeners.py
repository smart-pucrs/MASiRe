import jwt
import json

from src.communication.api_variables_holder import variables
from src.communication.events.emiters import on_response
from src.communication.events.controller import Controller


controller = Controller()
socketio = variables['socketio']


@socketio.on('first_message')
def respond_to_request_ready(message):
    """
        Receive the agent information encoded and decode it
        Add the decoded agent to a list insed the agent_manager
        Use the singleton to get the simulation instance and prevent from instantiating the class multiple times
        Call two responsed:
            First containing the agents_list
            Second containg the simulation pre step
    """
    
    response = ['ready', [{'can_connect': False}, {'data': None}]]

    agent = json.loads(message)

    if controller.check_population():
        agent_encoded = jwt.encode(agent, 'secret', algorithm='HS256').decode('utf-8')
        controller.agents[len(controller.agents)+1] = agent_encoded
        response[1][0]['can_connect'] = True
        response[1][1]['data'] = controller.agents[len(controller.agents)]

    on_response(response[0], json.dumps(response[1]))


@socketio.on('connect_agent')
def respond_to_request(message=''):
    """"
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

        Send to the agents the response from the method

        :param message: the JSON agent
        """

    response = ['connection_result', {'agent_connected': False}]

    if controller.check_agent(json.loads(message)):
        if controller.check_timer():
            response[1]['agent_connected'] = True

    on_response(response[0], json.dumps(response[1]))


@socketio.on('receive_jobs')
def handle_connection(message):
    """
    Receive all the jobs from the agents

    Instantiate the response considering that the result will be True
    Collect the JSON message and fit it on the agent variable
    If the handle_connection returns True
    Add the job to the jobs done list
    Emit response to the agent

    Else
    Emit response containing False to the agents

    :param message: the JSON agent
    """

    response = ['received_jobs_result', {'job_delivered': False}]

    message = json.loads(message)
    agent_method = (message['token'], (message['method'], message['parameters'][0], message['parameters'][1]))

    if controller.check_request(agent_method):
        controller.jobs[agent_method[0]] = (agent_method[1][0], agent_method[1][1], agent_method[1][2])
        response[1]['job_delivered'] = True

    on_response(response[0], json.dumps(response[1]))


@socketio.on('time_ended')
def finish_conection():
    """
    Due to limitations with Threads, this method is called when an external agent
    calculate the time and calls it
    """

    from src.simulation.manager.simulation_instance import SimulationSingleton

    token_id = {}
    count = 1
    for token in controller.jobs.keys():
        token_id[token] = count
        count += 1

    jobs = []
    for token in controller.jobs.keys():
        jobs.append((token_id[token], controller.jobs[token]))

    aux = SimulationSingleton().simulation_manager.do_step(jobs)

    for id, result in aux:
        token_outside = ''

        for token in token_id:
            if token_id[token] == id:
                token_outside = token
                break

        final_json = {'result': result, 'token': token_outside}

        on_response('connection_result', json.dumps(final_json))












