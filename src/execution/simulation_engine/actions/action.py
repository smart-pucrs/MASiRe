import logging
from abc import ABC, ABCMeta, abstractmethod
from ..exceptions.exceptions import FailedWrongParam, FailedParameterType, FailedNoMatch

logger = logging.getLogger(__name__)

class Mediator(ABC):    
    def notify(self, sender: object, event: str, params) -> None:
        pass
    def sync(self, sender: object, event: str, params):
        pass

class Action(object):
    __metaclass__ = ABCMeta

    def __init__(self, agent, skills, resources, parameters, type, min_args, max_args):
        logger.debug(f"action {type} created")
        self.agent = agent
        exec(f'self.agent.last_action = type')
        self.skills = skills
        self.resources = resources
        self.parameters = parameters
        self.type = type
        self.min_args = min_args 
        self.max_args = max_args
        self.mates = []
        self.error_message = ''

        self.validate_parameters()

    @property
    def mediator(self) -> Mediator:
        return self._mediator
    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator
    @property
    def is_ok(self) -> bool:
        return self.error_message == ''
    @property
    def need_sync(self) -> bool:
        return len(self.mates) > 0
    @property
    def result(self) -> dict:
        return {'agent': self.agent, 'message': self.error_message}   

    @abstractmethod
    def prepare(self):
        pass
    @abstractmethod
    def check_parameters(self):
        pass
    @abstractmethod
    def check_constraints(self):
        pass
    @abstractmethod
    def match(self, action):
        pass
    @abstractmethod
    def execute(self, map, nodes, events, tasks):
        pass

    def validate_parameters(self):
        try:
            if (len(self.parameters) < self.min_args or len(self.parameters) > self.max_args):
                raise FailedWrongParam(f'wrong number of parameters, expecting among {self.min_args} and {self.max_args} parameters')
        
            self.check_parameters()
        except Exception as e:            
            self._report_exception(e)

    def validate_constraints(self):        
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

    def do(self, map, nodes, events, tasks):   
        if self.error_message != '': return   

        try:               
            self.validate_constraints()

            new_state, exception = self.execute(map, nodes, events, tasks)
            exec(f'self.agent.last_action_result = "success"')

            for key, value in new_state.items():
                exec(f'self.agent.{key} = value')

            if exception != None:
                raise exception
        except Exception as e:
            self._report_exception(e)

    def _report_exception(self, e: Exception):
        logger.critical(e,exc_info=True)
        exec(f'self.agent.last_action_result = e.identifier')
        self.error_message = str(e)

    @staticmethod
    def create_action(agent, action, skills, resources, parameters):
        for subclass in Action.__subclasses__():
            if action.lower() in subclass.__name__.lower(): 
                return subclass(agent,skills,resources,parameters)

class SyncActions(Mediator):
    shared_memory = []
    def __init__(self, *actions: Action) -> None:
        self._expected_actions = 0
        self._actions = actions
        for act in self._actions:
            act.mediator = self
            name, qtd = act.mates[0]
            self._expected_actions = max(self._expected_actions, qtd+1)        
    
    def sync(self, map, nodes, events, tasks):          
        try:   
            if len(self._actions) < self._expected_actions: 
                raise FailedNoMatch('Missing agents to syncronise actions.')

            for act in self._actions: act.prepare() 

            for act in self._actions: act.validate_constraints() 

            for act in self._actions: act.execute(map, nodes, events, tasks)

            for act in self._actions:
                exec(f'act.agent.last_action_result = "success"')
        except Exception as e:            
            logger.critical(e,exc_info=True)
            for act in self._actions: 
                exec(f'act.agent.last_action_result = e.identifier')
                act.error_message = str(e)

    def results(self):
        return [act.result for act in self._actions]

    def notify(self, sender: Action, event: str, params) -> None:
        for act in self._actions:
            if act is not sender: 
                act.sync(sender, event, params)
