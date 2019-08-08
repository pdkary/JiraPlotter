import SprintData
import pandas as pd
import requests
import jira_resources.resources as rs


class BoardData:

    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.sprints = None
        self._velocity_df = None

    @property
    def velocity_df(self):
        if self.sprints is not None:
            return self.sprints.velocity_df
        else:
            return pd.DataFrame(columns=["name", "committed", "completed"])
    @velocity_df.setter
    def velocity_df(self, value):
        self._velocity_df = value

    @property
    def completed(self):
        return self.velocity_df["completed"].tolist()

    @property
    def committed(self):
        return self.velocity_df["committed"].tolist()

    def get_sprints(self):
        sprint_list = requests.get(rs.server + rs.chart_endpoint + str(self.id), auth=(rs.user_name, rs.api_token))
        self.sprints = SprintData(sprint_list)

    def to_json(self):
        return {
            'committed': self.velocity_df.as_matrix(columns=["committed"]).tolist(),
            'completed': self.velocity_df.as_matrix(columns=["completed"]).tolist(),
            'names': self.sprints.names}
