import os
import pathlib
import subprocess


class Handler:
    """Class that handles all the creation of the environment for tests."""

    def __init__(self):
        self.venv_path = None
        self.root = pathlib.Path(__file__).parents[3].absolute()

    def create_environment(self):
        """Install all dependencies created virtual environment."""

        venv_path = self.get_venv_path()

        if not os.path.exists(venv_path):
            try:
                subprocess.call(['virtualenv', 'venv'])
            except FileNotFoundError:
                FNULL = open(os.devnull, 'w')
                subprocess.call([f'pip', 'install', 'virtualenv'], stdout=FNULL,
                                stderr=subprocess.STDOUT)
                subprocess.call(['virtualenv', 'venv'], stdout=FNULL, stderr=subprocess.STDOUT)

        venv_path += '/' if not venv_path.find('/') else '\\'
        self.venv_path = venv_path

        self.install_requirements()

    def get_venv_path(self):
        """Return the path to the created virtual environment."""

        venv_path = self.root / 'venv'

        venv_path = venv_path / 'Scripts' if os.name == 'nt' else venv_path / 'bin'

        return str(venv_path.absolute())

    def install_requirements(self):
        """Install the requirements on the environment."""

        requirements_path = self.root / 'requirements.txt'
        FNULL = open(os.devnull, 'w')
        subprocess.call([f"{str(self.venv_path)}pip", "install", "-r", str(requirements_path.absolute())],
                        stdout=FNULL, stderr=subprocess.STDOUT)
