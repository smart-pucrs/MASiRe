
#Simulation boilerplate v1

class Simulation:
  #takes care of the current step sent by communication core
  
  step
  world
  generator
  actionExecutor ...

  init(json):
    pre_step(step)
    step(step, dict[str -> action])
    finish()
  
  finish():
  ...

class Agent:
  #keeps track of an agent attributes (according to its type)
    
  map[type -> resources]
    resources:
        battery
        speed
        capacities
        ...
    
  constructor(type):
  ...

class World:
  #configure routes, generate maps between bounds, take care of locations...
  
  agents
  events
  routes
  bounds(location) ...
  
  update():
  ...
  
  generate_map():
  ...
  
  create_route():
  ...

class Generator:
  #generates all events related to the current step

  bounds(steps)
  chances ...
  
  generate_event(chances, bounds):
  ...
  

class ActionExecutor:
  #evaluates the execution of an agent request and implement it

  execute(World world, Action action, Agent agent):
    world.update()
    ... 
 
  post_execute():
  ...
