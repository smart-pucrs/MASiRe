import argparse
import multiprocessing
import subprocess
from directory_path import dir as root


def start_simulation(s_args, python_version):
    file_path = root / "src" / "simulation_app.py"
    subprocess.call([f"python{python_version}", str(file_path), *map(str, s_args)])


def start_api(a_args, python_version):
    file_path = root / "src" / "api_app.py"
    subprocess.call([f"python{python_version}", str(file_path), *map(str, a_args)])


def install_requirements(python_version):
    subprocess.call([f"pip{python_version}", "install", "-r", "requirements.txt"])


def handle_arguments(parser):
    args = parser.parse_args()
    config_file_location = args.conf
    base_url = args.url
    simulation_port = args.sp
    api_port = args.ap
    pyv = args.pyv
    step_time = args.step_t
    first_conn_time = args.first_t

    if args.r:
        install_requirements(pyv)

    return [config_file_location, base_url, simulation_port], \
           [base_url, api_port, simulation_port, step_time, first_conn_time], \
           pyv


def create_parser():
    parser = argparse.ArgumentParser(prog='Disaster Simulator')
    parser.add_argument('-conf', required=True, type=str)
    parser.add_argument('-url', required=False, type=str, default='127.0.0.1')
    parser.add_argument('-sp', required=False, type=str, default='8910')
    parser.add_argument('-ap', required=False, type=str, default='12345')
    parser.add_argument('-pyv', required=False, type=str, default='')
    parser.add_argument('-r', required=False, type=bool, default=False)
    parser.add_argument('-step_t', required=False, type=int, default=30)
    parser.add_argument('-first_t', required=False, type=int, default=60)
    return parser


if __name__ == '__main__':
    parser_ = create_parser()
    simulation_args, api_args, pyv = handle_arguments(parser_)

    simulation = multiprocessing.Process(target=start_simulation, args=(simulation_args, pyv))
    api = multiprocessing.Process(target=start_api, args=(api_args, pyv))

    simulation.daemon = True
    api.daemon = True

    simulation.start()
    api.start()

    simulation.join()
    api.join()
