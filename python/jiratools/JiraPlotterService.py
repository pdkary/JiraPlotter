import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib
from jiratools.JiraDataService import JiraDataService
from datetime import datetime

matplotlib.use('agg')


class JiraPlotterService:

    def __init__(self, jira_data):
        self.jira_data = jira_data
        self.infostr_props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        self.xlim = self.jira_data.x_values.max() * 1.1
        self.ylim = max(self.jira_data.ciy_plus.max(), self.jira_data.y_values.max()) * 1.1

        self.count = self.jira_data.x_values.shape[0]
        self.shape = self.jira_data.x_values.shape
        self.x_space = np.linspace(0, self.xlim, self.count)

        self.ymax = np.ones(shape=self.shape) * self.ylim
        self.zeros = np.zeros(shape=self.shape)

        self.confidence_str = str(self.jira_data.confidence * 100)[:2]
        self.filesuffix = self.jira_data.qualifier if self.jira_data.qualifier != "" else "all"
        self.filepath = os.pardir + '/static/images/plot_' + self.filesuffix + "_" + self.confidence_str + "_" + self.dt_string + '.png'

    @property
    def dt_string(self):
        now = datetime.now()
        return now.strftime("%d-%m-%Y")

    @property
    def infostr(self):
        return "\n".join((
            r'$R^2=%.2f$' % self.jira_data.r_squared,
            r'$y = {0:.3g}x + {1:.3g}$'.format(self.jira_data.coefficients[0], self.jira_data.coefficients[1]),
            r'boards=%s' % ("\n              ".join([x.name for x in self.jira_data.boards]))
        ))

    def save(self):
        ax = plt.subplot(111)
        chartBox = ax.get_position()

        ax.plot(self.jira_data.committed, self.jira_data.completed, 'ro', label="data points")
        ax.plot(self.jira_data.x_values, self.jira_data.y_values, '-', color="blue", label="trendline")
        ax.plot(self.x_space, self.x_space, '--', color="grey", label="y=x")

        ax.set_position([chartBox.x0 * 0.8, chartBox.y0 * 2.50, chartBox.width * 0.8, chartBox.height * 0.8])

        ax.legend(loc='upper center',
                  bbox_to_anchor=(1.2, 1),
                  shadow=True,
                  ncol=1)

        ax.text(x=1.05,
                y=.7,
                s=self.infostr,
                verticalalignment="top",
                transform=ax.transAxes,
                bbox=self.infostr_props,
                fontsize=9)

        plt.fill_between(x=self.x_space,
                         y1=self.jira_data.ciy_plus,
                         y2=self.ymax,
                         where=self.ymax > self.jira_data.ciy_plus,
                         facecolor="#DDDDDD",
                         interpolate=True)

        plt.fill_between(x=self.x_space,
                         y1=self.zeros,
                         y2=self.jira_data.ciy_minus,
                         where=self.jira_data.ciy_minus > self.zeros,
                         facecolor="#DDDDDD",
                         interpolate=True)

        plt.xlim((0, self.xlim))
        plt.ylim((0, self.ylim))
        plt.grid()
        plt.title(
            "%s team story analysis with %s%% Confidence" % (self.jira_data.qualifier, self.confidence_str))
        plt.xlabel('Committed Stories')
        plt.ylabel("Completed Stories")

        plt.savefig(self.filepath)
        plt.close('all')


if __name__ == '__main__':
    plots = ["INT", "FIIXC"]
    jiraDataService = JiraDataService()
    for x in plots:
        jiraDataService.set_qualifier(x)
        jiraDataService.get_board_dict()
        jiraDataService.get_confidence()
        jiraDataService.prune()

        plotter = JiraPlotterService(jiraDataService)
        plotter.save()
