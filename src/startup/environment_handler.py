import os
import pathlib
import subprocess


class Handler:
    """Class that handles the creation and preparation of it to run the system.

    Note that this class was meant to be independent on operating system."""

    def __init__(self):
        self.venv_path = None
        self.root = pathlib.Path(__file__).parents[2].absolute()

    def create_environment(self, globally, python_version):
        """Install all dependencies on the chosen environment.

        The environment can be either the global interpreter or a fresh interpreter created with virtualenv.

        :param globally: Inform either install on the global interpreter or not.
        :param python_version: Python version installed on the user machine and chosen to be used."""

        if globally:
            self.install_requirements('', python_version)
            self.venv_path = ''

        else:
            venv_path = self.get_venv_path()

            if not os.path.exists(venv_path):
                FNULL = open(os.devnull, 'w')
                try:
                    subprocess.call(['virtualenv', 'venv'], stdout=FNULL)
                except FileNotFoundError:
                    subprocess.call([f'pip{python_version}', 'install', 'virtualenv'], stdout=FNULL,
                                    stderr=subprocess.STDOUT)
                    subprocess.call(['virtualenv', 'venv'], stdout=FNULL, stderr=subprocess.STDOUT)

            venv_path += '/' if not venv_path.find('/') else '\\'
            self.venv_path = venv_path

            self.install_requirements(venv_path, python_version)

    def get_venv_path(self):
        """Return the fresh interpreter path based on the operating system of the user machine.

        :returns str: Path to the interpreter that will be created with virtualenv."""

        venv_path = self.root / 'venv'

        venv_path = venv_path / 'Scripts' if os.name == 'nt' else venv_path / 'bin'

        return str(venv_path.absolute())

    def install_requirements(self, venv_path, python_version):
        """Install the requirements on the path given.

        If no path given, the requirements will be installed on the global interpreter informed by python_version.

        :param venv_path: Path to the interpreter.
        :param python_version: Python version chosen by the user."""

        requirements_path = self.root / 'requirements.txt'
        FNULL = open(os.devnull, 'w')
        subprocess.call([f"{str(venv_path)}pip{python_version}", "install", "-r", str(requirements_path.absolute())],
                        stdout=FNULL, stderr=subprocess.STDOUT)
