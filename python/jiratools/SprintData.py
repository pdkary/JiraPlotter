import pandas as pd


class SprintData:

    def __init__(self, jira_sprint_object):
        self.velocity_df = pd.DataFrame(columns=['name', 'committed', 'completed'])
        self.sprinfo = jira_sprint_object.json()
        self.names = [x["name"] for x in self.sprinfo["sprints"]]
        self.get_sprint_info()

    def get_sprint_info(self):
        for i, sprint in enumerate(self.sprinfo['sprints']):
            name = sprint["name"]
            id = str(sprint["id"])
            velocityStats = self.sprinfo["velocityStatEntries"][id]
            self.velocity_df.loc[i] = [name, velocityStats["estimated"]["value"], velocityStats["completed"]["value"]]
        self.velocity_df = self.velocity_df.set_index("name")
