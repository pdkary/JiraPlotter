from flask import Flask, request,send_file
from flask_cors import CORS
from jiratools.JiraDataService import JiraDataService
from jiratools.JiraPlotterService import JiraPlotterService
import json
import re

REGEX = "[^a-zA-Z0-9_ ]"

app = Flask(__name__)
CORS(app)
dataService = JiraDataService()


@app.route('/boards')
def get_boards():
    return json.dumps(dataService.board_names)


@app.route('/plot', methods=['GET', 'POST'], )
def plot_boards():
    if request.method == 'POST':
        data = [x for x in re.split(REGEX, str(request.data)) if len(x) > 1]
        dataService.get_board_dict(data)
        dataService.get_confidence()
        dataService.prune()

        plotter = JiraPlotterService(dataService)
        filedata = plotter.save()
        dataService.reinit()
        return send_file(filedata, mimetype='image/gif')
    else:
        return None


if __name__ == '__main__':
    app.run()
