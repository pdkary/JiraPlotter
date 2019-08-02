import jira
import requests
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import os
import matplotlib
import resources.resources as rs
from datatime import datetime

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
        self.board_dict = {}
        self.velocity_dict = {}
        self.velocity_dict_init()
        self.clean_velocity_dict()

    @property
    def boards(self):
        return [x for x in self.auth_jira.boards() if
                (self.qualifier.lower() in x.name.lower() and 'v' not in x.name.lower())]

    @property
    def committed(self):
        l = [self.velocity_dict[x]['committed'].tolist() for x in self.velocity_dict.keys()]
        return [item for sublist in l for item in sublist]

    @property
    def completed(self):
        l = [self.velocity_dict[x]['completed'].tolist() for x in self.velocity_dict.keys()]
        return [item for sublist in l for item in sublist]

    def analyze(self):
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

    def get_figure(self):
        if self.analyze():
            infostr = "\n".join((
                r'$R^2=%.2f$' % (self.Rsquared),
                r'$y = {0:.3g}x + {1:.3g}$'.format(self.coeffs[0], self.coeffs[1]),
                r'boards=%s' % ("\n              ".join([x.name for x in self.boards]))
            ))
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

            plt.plot(self.committed, self.completed, 'ro', label="data points")
            plt.plot(self.x_values, self.y_values, '-', color="blue", label="trendline")
            plt.plot(self.x_values, self.ciy_plus, '-', color="green", label="Upper CI")
            plt.plot(self.x_values, self.ciy_minus, '-', color="green", label="Lower CI")
            plt.plot(self.x_values, self.x_values, '--', color="grey", label="y=x")
            plt.xlabel('Committed Stories')
            plt.ylabel("Completed Stories")
            plt.grid()
            plt.legend()
            plt.text(max(self.x_values) * .7, min(self.ciy_minus), infostr, bbox=props)
            plt.title("%s team story analysis with %d%% Confidence" % (self.qualifier, self.confidence * 100))
            #get datetime
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y")
            # save to file
            filesuffix = self.qualifier if self.qualifier != "" else "all"
            filepath = os.pardir + '/static/images/plot_' + filesuffix + dt_string + '.png'
            plt.savefig(filepath)
            plt.close()

    def velocity_dict_init(self):
        print("\nGathering velocity information for " + self.qualifier)
        for x in self.boards:
            self.board_dict[x.name.split()[0]] = x
            self.velocity_dict[x.name.split()[0]] = pd.DataFrame(columns=['committed', 'completed'])

        for key in tqdm.tqdm(self.board_dict.keys()):
            board = self.board_dict[key]
            try:
                sprinfo = requests.get(rs.server + rs.chart_endpoint + str(board.id), auth=(rs.user_name, rs.api_token))
            except requests.exceptions.SSLError:
                print("You have reached your request limit, try again in a few minutes")
            for i, item in enumerate(sprinfo.json()['velocityStatEntries'].values()):
                self.velocity_dict[key].loc[i] = [item["estimated"]["value"], item["completed"]["value"]]

    def clean_velocity_dict(self):
        print("\nRemoving outliers and empty datasets")
        keys_to_delete = []
        for key in tqdm.tqdm(self.velocity_dict.keys()):
            if len(self.velocity_dict[key]["completed"]) == 0:
                keys_to_delete.append(key)
            else:
                df = self.velocity_dict[key]
                df = df[(np.abs(stats.zscore(df)) < self.outlier_zscore_threshold).all(axis=1)]
                self.velocity_dict[key] = df

        for x in keys_to_delete:
            del self.velocity_dict[x]


if __name__ == '__main__':
    plots = ["F"]
    j = [JiraPlotter(qualifier=x) for x in plots]
    for x in j:
        x.get_figure()
