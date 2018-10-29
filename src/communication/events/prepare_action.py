from flask import json

agents = []


def handle_request(agent):
    """
    Verify if there are still space to the new agent and if the agent was properly sent
    with all its parameters

    :param agent: object from JSON file
    :return: boolean
    """
    global agents

    if len(agents) < 5:
        if contain_parameters(agent):
            # if verify_json(agent):
            agents.append(agent)
            return True
    return False


def contain_parameters(agent):
    """
    Verify if the agent has any empty field in the request
    False if there are any empty field
    True if not
#
#     if not contain_parameters(agent):
#         return False
#
#     if not agent_is_present(agent, available_agents['agents']):
#         return False
#
#     return True

    :param agent
    :return boolean
    """

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
