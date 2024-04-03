from flask import Flask
from flask import jsonify, request
from config import AVAILABLE_TYPES
from utils import tasks_types


APP = Flask(__name__)


@APP.route('/')
def default() -> jsonify:
    return jsonify(status="200")


@APP.route('/task', methods=['POST'])
def task() -> jsonify:
    task_type = request.form["type"]
    img = request.files["image"]
    if task_type in AVAILABLE_TYPES:
        rec_task = tasks_types[task_type](image=img)
        response = rec_task.execute_task()

        return jsonify(response)
    else:
        return jsonify({"status": "error",
                        "types": ",".join(AVAILABLE_TYPES)})


if __name__ == '__main__':
    APP.run(threaded=True)
