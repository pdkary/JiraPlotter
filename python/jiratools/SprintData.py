from jiratools.VelocityFrame import VelocityFrame


class SprintData(VelocityFrame):
    """
    Encapsulates Data from all sprints within given object as a DataFrame
    """
    def __init__(self, sprint_list_obj):
        super().__init__()
        for i, sprint in enumerate(sprint_list_obj['sprints']):
            sprint_id = str(sprint["id"])
            name = sprint["name"]
            committed = sprint_list_obj["velocityStatEntries"][sprint_id]["estimated"]["value"]
            completed = sprint_list_obj["velocityStatEntries"][sprint_id]["completed"]["value"]
            self.add(name, committed, completed)

        self.df = self.df.set_index("name")