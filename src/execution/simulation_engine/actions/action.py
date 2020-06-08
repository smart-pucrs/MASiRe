import logging
from abc import ABC, ABCMeta, abstractmethod, abstractproperty
from ..exceptions.exceptions import MASiReException, FailedWrongParam, FailedParameterType, FailedNoMatch

logger = logging.getLogger(__name__)

class Mediator(ABC):    
    def notify(self, sender: object, event: str, params) -> None:
        pass
    def sync(self, sender: object, event: str, params):
        pass

class Action():
    __metaclass__=ABCMeta
    
    def __init__(self, agent, game_state, parameters: list, type: str, qtd_args: list):
        logger.debug(f"action {type} created")
        self.agent = agent
        exec(f'self.agent.last_action = type')
        self.skills = game_state.actions[type]['abilities']
        self.resources = game_state.actions[type]['resources']
        self.parameters = parameters
        self.type = type
        self.qtd_args = qtd_args 
        self.mates = []
        self.error_message = ''

        self.validate_parameters()

    @abstractproperty
    def action(self):
        raise NotImplementedError

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
    def check_constraints(self, map):
        pass
    @abstractmethod
    def match(self, action):
        pass
    @abstractmethod
    def execute(self, map, nodes, events, tasks):
        pass

    def validate_parameters(self):
        try:
            if len(self.parameters) not in self.qtd_args:
                raise FailedWrongParam(f'wrong number of parameters, expecting {self.qtd_args} parameters')
        
            self.check_parameters()
        except MASiReException as e:
            self._report_masire_exception(e)
        except Exception as e:            
            self._report_exception(e)

    def validate_constraints(self, map):        
        def check_demand(action_demands, agent_has):
            for demand in action_demands:
                it_is = all(s in agent_has for s in demand)
                if it_is: return it_is
            return False

        has_skills = check_demand(self.skills, self.agent.abilities)
        if not has_skills: raise FailedParameterType(f'The following skills are required: {self.skills}')
        
        has_resources = check_demand(self.resources, self.agent.resources)
        if not has_resources: raise FailedParameterType(f'The following resources are required: {self.resources}')

        self.check_constraints(map)

    def do(self, map, nodes, events, tasks):   
        if self.error_message != '': return   

        request = None
        try:               
            self.validate_constraints(map)

            # new_state, exception = self.execute(map, nodes, events, tasks)
            request = self.execute(map, nodes, events, tasks)
            self.agent.last_action_result = 'success'
                        
            # for key, value in new_state.items():
            #     exec(f'self.agent.{key} = value')

            # if exception != None:
            #     raise exception
        except MASiReException as e:
            self._report_masire_exception(e)
        except Exception as e:
            self._report_exception(e)
        
        return request

    def _report_masire_exception(self, e: MASiReException):
        logger.debug(e)
        self.agent.last_action_result = e.identifier
        self.error_message = str(e)
    def _report_exception(self, e: Exception):
        logger.critical(e,exc_info=True)
        self.agent.last_action_result = 'internalError' 
        self.error_message = str(e)

    @staticmethod
    def create_action(agent, action, game_state, parameters):
        for subclass in Action.__subclasses__():
            if action.lower() in subclass.action[0].lower() and len(parameters) in subclass.action[1]: 
                return subclass(agent,game_state,parameters)
        logger.error(f"{agent.token}'s action {action} was not found")
        return NoAction(agent, action)
            # if action.lower() in subclass.__name__.lower(): 
            #     return subclass(agent,game_state,parameters)

class NoAction():
    def __init__(self, agent, action):
        self.agent = agent
        self.agent.last_action = action
        self.agent.last_action_result = 'actionNotFound'
    @property
    def is_ok(self) -> bool:
        return False
    @property
    def result(self) -> dict:
        return {'agent': self.agent, 'message': f"{self.agent.last_action} not found check action's parameters"}

class SyncActions(Mediator):
    def __init__(self, *actions: Action) -> None:
        self.shared_memory = []
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

            for act in self._actions: act.validate_constraints(map) 

            for act in self._actions: act.execute(map, nodes, events, tasks)

            for act in self._actions:
                exec(f'act.agent.last_action_result = "success"')
        except MASiReException as e:
            logger.debug(e)
            for act in self._actions: 
                act.agent.last_action_result = e.identifier
                act.error_message = str(e)
        except Exception as e:            
            logger.critical(e,exc_info=True)
            for act in self._actions: 
                act.agent.last_action_result = 'internalError'
                act.error_message = str(e)
    
    def agents_same_location(self, map):
        location = self._actions[0].agent.location
        for act in self._actions:
            if not map.check_location(location, act.agent.location):
                return False
        return True

    def results(self):
        return [act.result for act in self._actions]

    def notify(self, sender: Action, event: str, params) -> None:
        return [act.sync(sender, event, params) for act in self._actions if act is not sender] 
        # for act in self._actions:
        #     if act is not sender: 
        #         act.sync(sender, event, params)
