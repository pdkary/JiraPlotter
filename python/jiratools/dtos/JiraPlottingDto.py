from JiraAnalysisDto import JiraAnalysisDto
import numpy as np
import scipy.stats as stats
import resources as rs


class JiraPlottingDto(JiraAnalysisDto):
    def __init__(self, analysisDto):
        self.__dict__ = analysisDto.__dict__
        st = min(self.committed) * .75
        end = max(self.committed) * 1.25

        self.x_values = np.arange(st, end, .5)
        self.y_values = self.trend_function(self.x_values)

        self.ciy_plus = self.y_values + self.confidence_interval(self.x_values, self.y_values)
        self.ciy_minus = self.y_values - self.confidence_interval(self.x_values, self.y_values)

    def trend_function(self, x):
        return self.coefficients[0] * x + self.coefficients[1]

    def confidence_interval(self, x, y):
        return stats.t.ppf(rs.confidence, self.n - 1) * self.std_err * np.sqrt(
            1 / self.n + ((x - self.xbar) ** 2) / self.SSx + (y - self.ybar) ** 2 / self.SSy)
