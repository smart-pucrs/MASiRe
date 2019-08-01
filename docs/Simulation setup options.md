### The simulation can be set with different flags from the command line, let's talk about each one here:

1. **-conf**: Represents the path for the configuration file. The path must be considered from the root of the project, which means that if the file is on a parent folder you need to put "../" for each parent. 

2. **-url**: It stands for the base URL that the simulation will be running, if the simulation will run on a server like "http://server.url/" it can be passed as an alternative to the localhost.

3. **-sp**: SP is the abreviation for simulation port, if wanted you can give the simulation a specific port to listen.

4. **-ap**: AP is the abreviation for API port, if wanted you can give the API a specific port to listen.

5. **-pyv**: The python version that you want to use. This flag is only necessary when more than one version of python is installed on the system. Note that unix already comes with python.

6. **-g**: If this flag is true than the global interpreter will be used. It can be usefull when you want to install all the dependencies on your machine.

7. **-step_t**: The time that the simulation will wait to finish each step. Note that the simulation will only wait this time if any agent decides to not send the action on that step, if all the agents send their actions, it will process them imediatelly.

8. **-first_t**: The time the simulation will wait for the agents to connect to it. Two important notes here, the first one is that the simulation will wait forever if no agent connects to it and it was supposed to, the second one is that if all the supposed agents connect to the simulation, it will start imediatelly. "Agent supposed to connect" means that at least one agent was put on the configuration file.

9. **-mtd**: Represents the method that the simulation will use to start it. Two methods are available, "time" and "button". If time is used, the simulation will wait for the agents to connect by time as discussed previously. If button is used, the user need to press a button when asked to do it, note that the simulation will start instantly after pressing the button and the agents will no longer be able to connect.

10. **-log**: If the user wants or not to save the log. Note that the log file is saved based on the datetime, which means that it will have a folder with the year number, a folder with the month name and finally the log file with the hour and minute the log was saved.

11. **-secret**: The secret that the simulation will use to communicate internally, since the ports can be seen from outside, this is a way to prevent intruders. It is no recommended to use this flag unless you know what you are doing.
