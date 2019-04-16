import multiprocessing
import subprocess
from directory_path import dir as root


def start_simulation():
    file_path = root / "simulation_app.py"
    subprocess.call(["python3", str(file_path)])


def start_api():
    file_path = root / "api_app.py"
    subprocess.call(["python3", str(file_path)])


if __name__ == '__main__':
    simulation = multiprocessing.Process(target=start_simulation)
    api = multiprocessing.Process(target=start_api)

    simulation.daemon = True
    api.daemon = True

    simulation.start()
    api.start()

    simulation.join()
    api.join()
