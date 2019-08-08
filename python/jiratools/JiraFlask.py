from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import JiraDataService
import JiraPlotterService
from JiraPlotlyService import JiraPlotlyService
import json
import re

REGEX = "[^a-zA-Z0-9_ ]"

app = Flask(__name__)
CORS(app)
dataService = JiraDataService()


@app.route('/boards')
def get_boards():
    return json.dumps(dataService.board_names)


@app.route('/plot', methods=['GET', 'POST'])
def plot_boards():
    if request.method == 'POST':
        dataService = get_data_service(request.data)
        plotter = JiraPlotterService(dataService)
        filedata = plotter.save()

        return send_file(filedata, mimetype='image/gif')
    else:
        return None

@app.route('/data')
def get_plot_data():
    dataService = get_data_service()
    plotly = JiraPlotlyService(dataService)
    return jsonify(plotly.get_json())

def get_data_service(alist):
    dataService.reinit()
    data = [x for x in re.split(REGEX, str(alist)) if len(x) > 1]
    dataService.get_board_dict(data)
    dataService.get_confidence()
    dataService.prune()
    return dataService


if __name__ == '__main__':
    app.run()
