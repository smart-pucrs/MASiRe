import requests
import time
from flask import Flask


app = Flask(__name__)


@app.route('/start', methods=['GET', 'POST'])
def start_timer():
    time.sleep(30)
    requests.post('http://localhost:12345/time_ended')


if __name__ == '__main__':
    app.run(port=5678)
