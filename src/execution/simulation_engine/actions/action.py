import logging
from abc import ABCMeta, abstractmethod
from ..exceptions.exceptions import FailedWrongParam, FailedParameterType

logger = logging.getLogger(__name__)

class Action(object):
    __metaclass__ = ABCMeta

    def __init__(self, agent, skills, resources, parameters, type, min_args, max_args):
        logger.debug(f"action {type} created")
        self.agent = agent
        self.skills = skills
        self.resources = resources
        self.parameters = parameters
        self.type = type
        self.min_args = min_args 
        self.max_args = max_args

    def _validate_parameters(self):
        if (len(self.parameters) < self.min_args or len(self.parameters) > self.max_args):
            raise FailedWrongParam(f'wrong number of parameters, expecting among {self.min_args} and {self.max_args} parameters')

        self.check_parameters()

    @abstractmethod
    def check_parameters(self):
        pass

    def _validate_constraints(self):        
        def check_demand(action_demands, agent_has):
            for demand in action_demands:
                it_is = all(s in agent_has for s in demand)
                if it_is: return it_is
            return False

        has_skills = check_demand(self.skills, self.agent.abilities)
        if not has_skills: raise FailedParameterType(f'The following skills are required: {self.skills}')
        
        has_resources = check_demand(self.resources, self.agent.resources)
        if not has_resources: raise FailedParameterType(f'The following resources are required: {self.resources}')

        self.check_constraints()

    @abstractmethod
    def check_constraints(self):
        pass

    def do(self, map, nodes, events):        
        self._validate_parameters()
        
        self._validate_constraints()

        new_state, exception = self.execute(map, nodes, events)

        for key, value in new_state.items():
            # agents_manager.edit(token, key, value)
            exec(f'self.agent.{key} = value')

        if exception != None:
            raise exception

    @abstractmethod
    def execute(self, map, nodes, events):
        pass



     