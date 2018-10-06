from flask import json


agents = []


def handle_request(agent):
    global agents

    if len(agents) < 5:
        if verify_json(agent):
            agents.append(agent)
            return 'agent added to jobs done list'
    return 'agent not added to jobs done list'


def verify_json(agent):

    f = open('agents.json', 'r').read()
    json_string = f.rstrip()
    available_agents = json.loads(json_string)

    if not contain_parameters(agent):
        return False

    if not agent_is_present(agent, available_agents['agents']):
        return False

    return True


def contain_parameters(agent):
    if agent[1][1] == '' or agent[1][1] is None:
        if agent[1][2] == '' or agent[1][2] is None:
            return False
        return False

    return True


def agent_is_present(agent, agents_list):
    for ag in agents_list:
        if ag['Name'] == agent[0]:
            return True

    return False

