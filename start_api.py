import os
import pathlib
from subprocess import run


# Here are setted the directory at venv where the python executable are
def start_api():
    interpreter_path = str(pathlib.Path(__file__).parent.absolute())

    # Windows based OS
    if os.name == 'nt':
        interpreter_path += '\\venv\\Scripts\\python.exe'

    # Linux based OS
    else:
        interpreter_path += "/venv/bin/python"

    run([str(interpreter_path), "-m", "flask", "run", "--host=0.0.0.0"],
        env=dict(FLASK_APP='src/communication/listeners.py', FLASK_ENV='production', FLASK_DEBUG='0', **os.environ))


if __name__ == '__main__':
    start_api()
