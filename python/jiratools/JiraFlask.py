from flask import Flask
from flask import request
from jiratools.JiraDataService import JiraDataService
import json

app = Flask(__name__)

dataService = JiraDataService()


@app.route('/boards')
def get_boards():
    return json.dumps(dataService.board_names)


@app.route('/plot', methods=['POST'])
def plot_boards():
    if request.method == 'POST':
        data = request.form
    else:
        return None


if __name__ == '__main__':
    app.run()
