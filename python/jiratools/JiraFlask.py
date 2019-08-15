from flask import Flask, request, send_file
from flask_cors import CORS
from JiraDataService import JiraDataService
from JiraPlotterService import JiraPlotterService
import JiraAnalysisService
import json
import re

REGEX = "[^a-zA-Z0-9_\\- ]"

app = Flask(__name__)
CORS(app)
print("gathering dataset")
dataService = JiraDataService()
print("done")

@app.route('/boards')
def get_boards():
    return json.dumps(dataService.names)


@app.route('/plot', methods=['GET', 'POST'])
def plot_boards():
    if request.method == 'POST':
        names = [x for x in re.split(REGEX, str(request.data)) if len(x) > 1]
        boards = dataService.get_by_names(names)
        plottingDto = JiraAnalysisService.get_plotting_dto(boards)
        plotter = JiraPlotterService(plottingDto,names)
        filedata = plotter.save()
        return send_file(filedata, mimetype='image/gif')
    else:
        return None


@app.route('/data', methods=["GET","POST"])
def get_plot_data():
    names = [x for x in re.split(REGEX, request.data) if len(x) > 1]
    boards = dataService.get_by_names(names)
    return JiraAnalysisService.get_analysis_dto(boards)


def run():
    app.run()


if __name__ == "__main__":
    app.run()
