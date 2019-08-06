import jira
import resources.resources as rs
import tqdm
from jiratools.BoardData import BoardData
import numpy as np
import scipy.stats as stats

options = {
    'server': rs.server
}


class JiraDataService:
    def __init__(self, confidence=.80, threshold=3):
        self.outlier_zscore_threshold = threshold
        self.confidence = confidence
        self.qualifier = ""
        self.auth_jira = jira.JIRA(options=options, basic_auth=(rs.user_name, rs.api_token))
        self.board_dict = {}
        self.r_squared = 0
        self.x_values = None
        self.y_values = None
        self.coefficients = None
        self.ciy_plus = None
        self.ciy_minus = None
        self.trend_function = None

    @property
    def boards(self):
        return [x for x in self.auth_jira.boards() if
                (self.qualifier.lower() in x.name.lower())]

    @property
    def board_names(self):
        return [x.name for x in self.boards]

    @property
    def committed(self):
        if not self.empty:
            l = [self.board_dict[x].velocity_df['committed'].tolist() for x in self.board_dict.keys()]
            return [item for sublist in l for item in sublist]
        else:
            return []

    @property
    def completed(self):
        if not self.empty:
            l = [self.board_dict[x].velocity_df['completed'].tolist() for x in self.board_dict.keys()]
            return [item for sublist in l for item in sublist]
        else:
            return []

    @property
    def empty(self):
        return self.board_dict is {}

    def set_qualifier(self, qualifier):
        self.qualifier = qualifier
        self.board_dict = {}

    def set_confidence(self, confidence):
        self.confidence = confidence

    def set_threshold(self, threshold):
        self.outlier_zscore_threshold = threshold

    def get_board_dict(self, boards_to_search=None):
        boards_to_search = self.boards if boards_to_search is None else boards_to_search
        print("\nGathering velocity information for " + self.qualifier)
        for x in tqdm.tqdm(boards_to_search):
            self.board_dict[x.name] = BoardData(x.name, x.id)
            self.board_dict[x.name].get_sprints()

    def get_confidence(self):
        if len(self.committed) == 0:
            return
        n = len(self.completed)
        df = len(self.committed) - 1
        st = min(self.committed) * .9
        end = max(self.committed) * 1.1
        xbar = sum(self.committed) / n
        ybar = sum(self.completed) / n

        self.x_values = np.arange(st, end, .5)
        self.coefficients, SSRes, rank, sing, rcond = np.polyfit(self.committed, self.completed, 1, full=True)
        self.trend_function = lambda x: self.coefficients[0] * x + self.coefficients[1]
        self.y_values = self.trend_function(self.x_values)

        SSy = sum([(self.completed[i] - ybar) ** 2 for i in range(n)])
        SSx = sum([(self.committed[i] - xbar) ** 2 for i in range(n)])

        std_error_estimate = np.sqrt(
            (sum([(x - xbar) ** 2 for x in self.committed]) + sum([(y - ybar) ** 2 for y in self.completed])) / (n - 1))

        confidence_interval = lambda x, y: stats.t.ppf(self.confidence, df) * std_error_estimate * np.sqrt(
            1 / n + ((x - xbar) ** 2) / SSx + (y - ybar) ** 2 / SSy)

        self.ciy_plus = self.y_values + confidence_interval(self.x_values, self.y_values)
        self.ciy_minus = self.y_values - confidence_interval(self.x_values, self.y_values)

        self.r_squared = 1 - SSRes / np.sqrt(SSy ** 2 + SSx ** 2)

    def prune(self):
        print("\nRemoving outliers and empty datasets")
        for board_name in tqdm.tqdm(self.board_dict.keys()):
            board = self.board_dict[board_name]
            if not board.velocity_df.empty:
                board.velocity_df = board.velocity_df[(board.velocity_df.T != 0).any()]
                board.velocity_df = board.velocity_df[
                    (np.abs(stats.zscore(board.velocity_df)) < self.outlier_zscore_threshold).all(axis=1)]
