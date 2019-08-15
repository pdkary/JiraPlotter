import pandas as pd
import numpy as np
import scipy.stats as stats
import resources as rs
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

    def prune(self):
        if not self.empty:
            self.df = self.df[(self.df.T != 0).any()]
            self.df = self.df[(np.abs(stats.zscore(self.df)) < rs.zscore).all(axis=1)]

    def to_json(self):
        return {
            'committed': self.committed.tolist(),
            'completed': self.completed.tolist(),
            'names': self.names}