import jira
import tqdm
from BoardData import BoardData
import JiraAnalysisService
import numpy as np
import scipy.stats as stats
import resources as rs

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
        self.ciy_plus = None
        self.ciy_minus = None
        self.analysis_dto = None
        self.x_values = []
        self.y_values = []

    def reinit(self):
        self.board_dict = {}
        self.used_boards = []
        self.ciy_plus = None
        self.ciy_minus = None
        self.analysis_dto = None
        self.x_values = []
        self.y_values = []

    @property
    def jira_boards(self):
        return [x for x in self.auth_jira.boards() if "v2" not in x.name and "v3" not in x.name and "v4" not in x.name]

    @property
    def boards(self):
        return self.board_dict.values()

    @property
    def board_names(self):
        return [x.name for x in self.jira_boards]

    @property
    def data_boards(self):
        return [x for x in self.board_dict.values() if not x.empty]

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
        self.analysis_dto = JiraAnalysisService.analyze(self.boards)

        n = len(self.analysis_dto.committed)
        df = n - 1
        st = min(self.analysis_dto.committed)*.75
        end = max(self.analysis_dto.committed)*1.25
        trend_function = lambda x: self.analysis_dto.coefficients[0] * x + self.analysis_dto.coefficients[1]

        self.x_values = np.arange(st, end, .5)
        self.y_values = trend_function(self.x_values)

        confidence_interval = lambda x, y: stats.t.ppf(self.confidence, df) * self.analysis_dto.std_err * np.sqrt(
            1 / n + ((x - self.analysis_dto.xbar) ** 2) / self.analysis_dto.SSx + (y - self.analysis_dto.ybar) ** 2 / self.analysis_dto.SSy)

        self.ciy_plus = self.y_values + confidence_interval(self.x_values, self.y_values)
        self.ciy_minus = self.y_values - confidence_interval(self.x_values, self.y_values)

    def prune(self):
        print("\nRemoving outliers and empty datasets")
        for board_name in tqdm.tqdm(self.board_dict.keys()):
            board = self.board_dict[board_name]
            if not board.velocity_df.empty:
                board.velocity_df = board.velocity_df[(board.velocity_df.T != 0).any()]
                board.velocity_df = board.velocity_df[
                    (np.abs(stats.zscore(board.velocity_df)) < self.outlier_zscore_threshold).all(axis=1)]
