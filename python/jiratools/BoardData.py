from jiratools.SprintData import SprintData
import requests
import resources.resources as rs
import pandas as pd


class BoardData:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.sprints = None
        self._velocity_df = None

    def get_sprints(self):
        sprint_list = requests.get(rs.server + rs.chart_endpoint + str(self.id), auth=(rs.user_name, rs.api_token))
        self.sprints = SprintData(sprint_list)

    @property
    def velocity_df(self):
        if self.sprints is not None:
            return self.sprints.velocity_df
        else:
            return pd.DataFrame(columns=["name", "committed", "completed"])

    @velocity_df.setter
    def velocity_df(self, value):
        self._velocity_df = value
