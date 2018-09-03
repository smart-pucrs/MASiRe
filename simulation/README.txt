class Simulation:

  int step
  World world
  Generator generator
  ActionExecutor actionExecutor

  init(JSON config)
  pre_step(int step)
  step(int step, dict(str -> action))
  finish()

class World:

  # world state

class Generator:

  double bounds
  double chances

class ActionExecutor:

  execute(World world, Action action, Agent agent)
  post_execute()
