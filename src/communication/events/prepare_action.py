from flask import json


def verify_method(method, agent):
    if method == 'deliver_virtual':
        return deliver_physical_load(agent)

    elif method == 'deliver_physical':
        return deliver_physical_load(agent)

    elif method == 'photograph':
        return post_photograph(agent)

    elif method == 'analyze_photo':
        return analyze_photo(agent)

    elif method == 'rescue victim':
        return rescue_victim(agent)

    elif method == 'collect water':
        return collect_water_sample(agent)

    elif method == 'move':
        return move(agent)


# ================= Virtual load function ============= #
def deliver_virtual_load(agent):
    return handle_request(agent)


# ================ Physical load function ============== #
def deliver_physical_load(agent):
    return handle_request(agent)


# ================== Photograph functions =============== #
def post_photograph(agent):
    return handle_request(agent)


def analyze_photo(agent):
    return handle_request(agent)


# ===================== Victim function ================= #
def rescue_victim(agent):
    return handle_request(agent)


# =================== Water function ================= #
def collect_water_sample(agent):
    return handle_request(agent)


# ============== Move function ============= #
def move(agent):
    return handle_request(agent)


def handle_request(agent):
    if verify_json(agent):
        agents.append(agent)
        return 'agent added to done jobs list'


def verify_json(agent):
    f = open('agents.json', 'r').read()
    json_string = f.rstrip()
    available_agents = json.loads(json_string)

    if agent['parameters'] == '' or agent['parameters'] is None:
        return False

    if not agent_is_present(agent, available_agents['agents']):
        return False

    return True


def agent_is_present(agent, agents_list):
    for ag in agents_list:
        if ag['Name'] == agent['id']:
            return True

    return False
