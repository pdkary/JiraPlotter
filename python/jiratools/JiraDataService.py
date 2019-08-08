import jira
import tqdm
import BoardData
import numpy as np
import scipy.stats as stats
import jira_resources as rs

options = {
    'server': rs.server
}


class JiraDataService:
    def __init__(self, confidence=.80, threshold=3):
        self.outlier_zscore_threshold = threshold
        self.confidence = confidence
        self.auth_jira = jira.JIRA(options=options, basic_auth=(rs.user_name, rs.api_token))
        self.board_dict = {}
        self.used_boards = []
        self.r_squared = 0
        self.x_values = None
        self.y_values = None
        self.coefficients = None
        self.ciy_plus = None
        self.ciy_minus = None
        self.trend_function = None

    def reinit(self):
        self.board_dict = {}
        self.used_boards = []
        self.r_squared = 0
        self.x_values = None
        self.y_values = None
        self.coefficients = None
        self.ciy_plus = None
        self.ciy_minus = None
        self.trend_function = None

    @property
    def jira_boards(self):
        return [x for x in self.auth_jira.boards() if "v2" not in x.name and "v3" not in x.name and "v4" not in x.name]

    @property
    def boards(self):
        return [x for x in self.board_dict.values()]

    @property
    def board_names(self):
        return [x.name for x in self.jira_boards]

    @property
    def all_committed(self):
        if not self.empty:
            l = [x.committed for x in self.boards]
            return [item for sublist in l for item in sublist]
        else:
            return []

    @property
    def all_completed(self):
        if not self.empty:
            l = [x.completed for x in self.boards]
            return [item for sublist in l for item in sublist]
        else:
            return []

    @property
    def empty(self):
        return self.board_dict is {}

    def set_confidence(self, confidence):
        self.confidence = confidence

    def set_threshold(self, threshold):
        self.outlier_zscore_threshold = threshold

    def get_board_dict(self, boards_to_search=None):
        self.used_boards = [x for x in self.jira_boards if
                            x.name in boards_to_search] if boards_to_search is not None else self.jira_boards

        for x in tqdm.tqdm(self.used_boards):
            print("\nGathering velocity information for " + x.name)
            self.board_dict[x.name] = BoardData(x.name, x.id)
            self.board_dict[x.name].get_sprints()

    def get_confidence(self):
        if len(self.all_committed) == 0:
            return
        n = len(self.all_completed)
        df = len(self.all_committed) - 1
        st = min(self.all_committed) * .9
        end = max(self.all_committed) * 1.1
        xbar = sum(self.all_committed) / n
        ybar = sum(self.all_completed) / n

        self.x_values = np.arange(st, end, .5)
        self.coefficients, SSRes, rank, sing, rcond = np.polyfit(self.all_committed, self.all_completed, 1, full=True)
        self.trend_function = lambda x: self.coefficients[0] * x + self.coefficients[1]
        self.y_values = self.trend_function(self.x_values)

        SSy = sum([(self.all_completed[i] - ybar) ** 2 for i in range(n)])
        SSx = sum([(self.all_committed[i] - xbar) ** 2 for i in range(n)])

        std_error_estimate = np.sqrt(
            (sum([(x - xbar) ** 2 for x in self.all_committed]) + sum(
                [(y - ybar) ** 2 for y in self.all_completed])) / (n - 1))

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
