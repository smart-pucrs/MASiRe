import time
from communication.objects.agent import Agent


class AgentsManager:
    """Class that will handle all the changes on agents. Every change on agents must be done here."""

    def __init__(self):
        self.agents = {}

    def add_agent(self, token, agent_info):
        """Add an agent to the dictionary.

        The key is the generated token and the value if the Agent object.

        :param token: The generated token for the agent.
        :param agent_info: The information sent to the API by the agent."""

        self.agents[token] = Agent(token, agent_info)

    def get_agent(self, token):
        """Get the agent object if the token is registered.

        :param token: The generated token for the agent requested.
        :return Agent|None: The registered agent or None if it was not registered."""

        return self.agents.get(token)

    def get_agents(self):
        """Get all the registered agents.

        :return list: All the agents objects."""

        return list(self.agents.values())

    def get_actions(self):
        """Return a list of all the actions that the agents have sent to the simulation on the previous step.

        Note: RuntimeError can occur if the gap between validating the action and ending the step occur, to prevent that,
        it will wait one second after the error and then proceed. If the error happens again, then it must be some
        internal error that are allowing the agents to send actions after the step is finished.

        :return list: All the actions sent on the previous step."""

        actions = []
        try:
            for token in self.agents:
                if self.agents[token].worker:
                    action_name = self.agents[token].action_name
                    action_params = self.agents[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        except RuntimeError:
            time.sleep(1)
            actions = []
            for token in self.agents:
                if self.agents[token].worker:
                    action_name = self.agents[token].action_name
                    action_params = self.agents[token].action_params

                    actions.append({'token': token, 'action': action_name, 'parameters': action_params})

        return actions

    def get_workers(self):
        """Get all the workers. The agent is considered a worker if it sent an action on the previous step.

        :return list: All the agents objects."""

        return [self.agents[token] for token in self.agents if self.agents[token].worker]

    def edit_agent(self, token, attribute, new_value):
        """Edit an attribute of some agent.

        :param token: The token of some agent that will be edited.
        :param attribute: The attribute of the agent that will be edited.
        :param new_value: The new value for the attribute given."""

        exec(f'self.agents[token].{attribute} = new_value')

    def clear_workers(self):
        """Clear all the workers. After the end of the step, all the workers are cleared so they have to send actions
        on the next step."""

        for token in self.agents:
            self.agents[token].worker = False

    def remove_agent(self, token):
        """Remove an agent from the dictionary.

        :param token: The generated token that will be removed from the dictionary."""

        del self.agents[token]
