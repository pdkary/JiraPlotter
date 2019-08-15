from frames.VelocityFrame import VelocityFrame
import requests
import resources as rs
import json


class SprintData(VelocityFrame):
    """
    Encapsulates Data from all sprints within given object as a DataFrame
    """
    def __init__(self, board_id):
        super().__init__()
        sprint_obj = self.get_data(board_id)
        for i, sprint in enumerate(sprint_obj['sprints']):
            sprint_id = str(sprint["id"])
            name = sprint["name"]
            committed = sprint_obj["velocityStatEntries"][sprint_id]["estimated"]["value"]
            completed = sprint_obj["velocityStatEntries"][sprint_id]["completed"]["value"]
            self.add(name, committed, completed)

        self.df = self.df.set_index("name")

    def get_data(self, board_id):
        return json.loads(requests.get(rs.server + rs.chart_endpoint + str(board_id),
                            auth=(rs.user_name, rs.api_token)).text)
