import pandas as pd


class VelocityFrame:
    def __init__(self):
        self.df = pd.DataFrame(columns=["name", "committed", "completed"])

    def add(self, name, committed, completed):
        self.df = self.df.append({"name": name, "committed": committed, "completed": completed}, ignore_index=True)

    @property
    def committed(self):
        return self.df["committed"]

    @property
    def completed(self):
        return self.df["completed"]

    @property
    def names(self):
        return self.df["names"]

    @property
    def empty(self):
        return not self.committed.any() and not self.completed.any()

    def to_json(self):
        return {
            'committed': self.committed.tolist(),
            'completed': self.completed.tolist(),
            'names': self.names}