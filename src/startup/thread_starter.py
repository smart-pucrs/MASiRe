import json
import pathlib
import subprocess
from multiprocessing import Process
from src.startup.environment_handler import Handler
from src.startup.arguments_parser import Parser
from src.startup.configuration_checker import Checker


class Starter:
    """Class that handles all the startup of the system.

    It makes use of other classes to prepare the environment to run the system.

    When the system is running, there is no safe way to stop it without waiting the end, if it stops before finishing the
    processes, there is a risk that they were not closed along with this class."""

    def __init__(self):
        self.parser = Parser()
        self.env_handler = Handler()
        self.checker = Checker(self.parser.get_argument('conf'))
        self.root = pathlib.Path(__file__).parents[1].absolute()

    def start(self):
        """Main function to start the hole system.

        Three main steps are defined here:
        1 - Check if the configuration file was properly made
        2 - Prepare the environment, either creating another interpreter or using the global one
        3 - Start the processes that will run the API and Simulation."""

        self.check_configuration_file()
        self.check_arguments()
        self.create_environment()
        arguments = self.get_arguments()
        self.start_processes(*arguments)

    def check_configuration_file(self):
        """Do all the verifications on the configuration file.

        if any errors are found on the configuration file: exits the program with the appropriate message."""

        result = self.checker.run_all_tests()
        if not result[0]:
            exit(result[1])

    def check_arguments(self):
        """Do all the verifications on the arguments.

        if any errors are found on the arguments: exits the program with the appropriate message."""

        test = self.parser.check_arguments()
        if not test[0]:
            exit(test[1])

    def create_environment(self):
        """Prepare the global environment or create one and prepare it.

        The user needs to inform if they want to use the global interpreter, otherwise another one will be created
        an used.

        If there are more than one version installed, the user needs to inform the correct one."""

        globally = self.parser.get_argument('g')
        python_version = self.parser.get_argument('pyv')

        self.env_handler.create_environment(globally, python_version)

    def get_arguments(self):
        """Get the arguments for the API and the Simulation.

        :returns list: All the necessary arguments to run the API.
        :returns list: All the necessary arguments to run the Simulation.
        :returns str: The python version informed by the user."""

        self.parser.check_arguments()

        config_file = self.parser.get_argument('conf')
        config_file = pathlib.Path(__file__).parents[2] / config_file

        with open(config_file, 'r') as configuration_file:
            json_file = json.load(configuration_file)
            agents_amount = sum([json_file['agents'][role]['amount'] for role in json_file['agents']])
            assets_amount = sum([json_file['socialAssets'][prof]['amount'] for prof in json_file['socialAssets']])

        simulation_arguments = self.parser.get_simulation_arguments()

        api_arguments = self.parser.get_api_arguments()
        api_arguments.append(agents_amount)
        api_arguments.append(assets_amount)

        return api_arguments, simulation_arguments, self.parser.get_argument('pyv')

    def start_processes(self, api_arguments, simulation_arguments, python_version):
        """Start the process that will run the API and the other process that will run the Simulation.

        Note that this method only returns when the processes end."""

        simulation_path = str((self.root / 'execution' / 'simulation.py').absolute())
        simulation_process_arguments = (simulation_path, simulation_arguments, self.env_handler.venv_path, python_version)
        simulation_process = Process(target=self.start_simulation, args=simulation_process_arguments, daemon=True)

        api_path = str((self.root / 'execution' / 'api.py').absolute())
        api_process_arguments = (api_path, api_arguments, self.env_handler.venv_path, python_version)
        api_process = Process(target=self.start_api, args=api_process_arguments, daemon=True)

        api_process.start()
        simulation_process.start()

        api_process.join()
        simulation_process.join()

    @staticmethod
    def start_simulation(module_path, simulation_arguments, venv_path, python_version):
        """Start the Simulation by command line."""

        subprocess.call([f'{str(venv_path)}python{python_version}', module_path, *map(str, simulation_arguments)])

    @staticmethod
    def start_api(module_path, api_arguments, venv_path, python_version):
        """Start the API by command line."""

        subprocess.call([f"{str(venv_path)}python{python_version}", module_path, *map(str, api_arguments)])
