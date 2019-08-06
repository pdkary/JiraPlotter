import jira
import requests
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
import matplotlib
import resources.resources as rs
from datetime import datetime
from jiratools.BoardData import BoardData

matplotlib.use('agg')
options = {
    'server': rs.server
}


class JiraPlotter:

    def __init__(self, qualifier="", confidence=.80, threshold=3):
        self.outlier_zscore_threshold = threshold
        self.qualifier = qualifier
        self.confidence = confidence
        self.auth_jira = jira.JIRA(options=options, basic_auth=(rs.user_name, rs.api_token))
        self.infostr_props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.board_dict = {}

    @property
    def boards(self):
        return [x for x in self.auth_jira.boards() if
                (self.qualifier.lower() in x.name.lower() and 'v' not in x.name.lower())]

    @property
    def committed(self):
        l = [self.board_dict[x].velocity_df['committed'].tolist() for x in self.board_dict.keys()]
        return [item for sublist in l for item in sublist]

    @property
    def completed(self):
        l = [self.board_dict[x].velocity_df['completed'].tolist() for x in self.board_dict.keys()]
        return [item for sublist in l for item in sublist]

    @property
    def infostr(self):
        return "\n".join((
            r'$R^2=%.2f$' % self.Rsquared,
            r'$y = {0:.3g}x + {1:.3g}$'.format(self.coeffs[0], self.coeffs[1]),
            r'boards=%s' % ("\n              ".join([x.name for x in self.boards]))
        ))

    def get_board_dict(self):
        board_dict = {}
        print("\nGathering velocity information for " + self.qualifier)
        for x in tqdm.tqdm(self.boards):
            board_dict[x.name] = BoardData(x.name, x.id)
            board_dict[x.name].get_sprints()
        self.board_dict = board_dict
        return board_dict

    def get_confidence(self):
        if len(self.committed) == 0:
            return False
        n = len(self.completed)
        df = len(self.committed) - 1
        st = min(self.committed) * .9
        end = max(self.committed) * 1.1
        xbar = sum(self.committed) / n
        ybar = sum(self.completed) / n

        self.x_values = np.arange(st, end, .5)
        self.coeffs, SSRes, rank, sing, rcond = np.polyfit(self.committed, self.completed, 1, full=True)
        self.trend_function = lambda x: self.coeffs[0] * x + self.coeffs[1]
        self.y_values = self.trend_function(self.x_values)

        SSy = sum([(self.completed[i] - ybar) ** 2 for i in range(n)])
        SSx = sum([(self.committed[i] - xbar) ** 2 for i in range(n)])

        std_error_estimate = np.sqrt(
            (sum([(x - xbar) ** 2 for x in self.committed]) + sum([(y - ybar) ** 2 for y in self.completed])) / (n - 1))

        confidence_interval = lambda x, y: stats.t.ppf(self.confidence, df) * std_error_estimate * np.sqrt(
            1 / n + ((x - xbar) ** 2) / SSx + (y - ybar) ** 2 / SSy)

        self.ciy_plus = self.y_values + confidence_interval(self.x_values, self.y_values)
        self.ciy_minus = self.y_values - confidence_interval(self.x_values, self.y_values)

        self.Rsquared = 1 - SSRes / np.sqrt(SSy ** 2 + SSx ** 2)
        return True

    def prune(self):
        print("\nRemoving outliers and empty datasets")
        for board_name in tqdm.tqdm(self.board_dict.keys()):
            board = self.board_dict[board_name]
            if not board.velocity_df.empty:
                board.velocity_df = board.velocity_df[(board.velocity_df.T != 0).any()]
                board.velocity_df = board.velocity_df[
                    (np.abs(stats.zscore(board.velocity_df)) < self.outlier_zscore_threshold).all(axis=1)]

    def get_figure(self):
        if self.get_confidence():
            xlim = self.x_values.max() * 1.1
            ylim = max(self.ciy_plus.max(), self.y_values.max()) * 1.1
            count = self.x_values.shape[0]
            shape = self.x_values.shape

            x = np.linspace(0, xlim, count)
            ymax = np.ones(shape=shape) * ylim
            zeros = np.zeros(shape=shape)

            fig = plt.figure()
            ax = plt.subplot(111)
            chartBox = ax.get_position()

            ax.plot(self.committed, self.completed, 'ro', label="data points")
            ax.plot(self.x_values, self.y_values, '-', color="blue", label="trendline")
            ax.plot(x, x, '--', color="grey", label="y=x")

            ax.set_position([chartBox.x0*0.8, chartBox.y0*2.50, chartBox.width * 0.8, chartBox.height*0.8])
            ax.legend(loc='upper center', bbox_to_anchor=(1.2, 1), shadow=True, ncol=1)
            ax.text(1.05, .7, self.infostr, verticalalignment="top", transform=ax.transAxes, bbox=self.infostr_props,
                    fontsize=9)

            plt.fill_between(x, self.ciy_plus, ymax, where=ymax > self.ciy_plus, facecolor="#DDDDDD",
                             interpolate=True)
            plt.fill_between(x, zeros, self.ciy_minus, where=self.ciy_minus > zeros, facecolor="#DDDDDD",
                             interpolate=True)
            plt.xlim((0, xlim))
            plt.ylim((0, ylim))
            plt.grid()
            plt.title("%s team story analysis with %d%% Confidence" % (self.qualifier, self.confidence * 100))
            plt.xlabel('Committed Stories')
            plt.ylabel("Completed Stories")
            # get datetime
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y")
            # save to file
            filesuffix = self.qualifier if self.qualifier != "" else "all"
            filepath = os.pardir + '/static/images/plot_' + filesuffix + "_" + str(
                self.confidence * 100) + "_" + dt_string + '.png'
            plt.savefig(filepath)
            plt.close()


if __name__ == '__main__':
    plots = ["", "FM"]
    j = [JiraPlotter(qualifier=x) for x in plots]
    for x in j:
        x.get_board_dict()
        x.get_figure()
