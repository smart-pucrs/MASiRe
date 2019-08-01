### Important points to be considered before using the simulation:

1. The simulation run based on steps, which means that it will generate N steps containing dictionaries, if you have memory problems the number of steps can be the problem, to solve this you can run the simulation with the same map multiple times, it is not the most appropriate solution but is a workaround if it is necessary this enormous amount of steps.

2. The responses from the simulation will change for assets and agents, except when errors occur. Handle the errors before trying to manipulate the data sent. An example is that when the agent is not found on the response from the simulation, it will return only the status, empty event and a message to help understant why this happened.

3. All the information from inside the engine will be kept inside the engine. Everything that comes out is just a copy of the actual data, it is not supposed to cause memory problems since it will not copy great amount of data, just the necessary to inform the agent what happened and why on each step.

4. The log from the simulation will only be saved when it finished. If the simulation stops for any reason, all the log will be lost. Note that stops means that an error occurred and was not caught or the user intentionally stopped it. Also note that uncaught errors will appear on the terminal.

5. Since the simulation is based on steps, the configuration file will represent a step, which means that the amount of victims, photos and water samples will be by step which means that a simulation configured with ten victims and ten steps will generate a hundred victims, the same for photos and water samples.

6. The simulation have two important parts, one is the API where all the agents and assets will interact and another is the engine where will handle all the calls from the API to execute inside the simulation. This structure was made to prevent the use of singletons and complexities that was not necessary. Due to this structure the simulation needs an extra port to communicate. The communication between the engine and the API is done by http requests.