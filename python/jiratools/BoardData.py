from SprintData import SprintData
from jiratools.VelocityFrame import VelocityFrame
import requests
import resources as rs
import json


class BoardData(SprintData):

    def __init__(self, name, board_id):
        super().__init__(self.get_data(board_id))
        self.name = name
        self.board_id = board_id

    def get_data(self, board_id):
        sprint_response = requests.get(rs.server + rs.chart_endpoint + str(board_id),
                                       auth=(rs.user_name, rs.api_token))
        return json.loads(sprint_response.text)
