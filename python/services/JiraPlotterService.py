import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib
from datetime import datetime
import resources as rs

matplotlib.use('agg')


class JiraPlotterService:

    def __init__(self, plotting_dto, board_names):
        self.board_names = board_names
        self.plotting_dto = plotting_dto
        self.confidence_str = str(rs.confidence * 100)[:2]

        filesuffix = self.get_file_name()
        self.filepath = os.getcwd() + '/static/images/plot_' + filesuffix

        self.infostr_props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        self.xlim = plotting_dto.x_values.max() * 1.25
        self.ylim = max(plotting_dto.ciy_plus.max(), plotting_dto.y_values.max()) * 1.25

        self.count = plotting_dto.x_values.shape[0]
        self.shape = plotting_dto.x_values.shape
        self.x_space = np.linspace(0, self.xlim, self.count)

        self.ymax = np.ones(shape=self.shape) * self.ylim
        self.zeros = np.zeros(shape=self.shape)

    @property
    def now_string(self):
        now = datetime.now()
        return now.strftime("%d-%m-%Y")

    @property
    def infostr(self):
        return "\n".join((
            r'$R^2=%.2f$' % self.plotting_dto.r_squared,
            r'$y = {0:.3g}x + {1:.3g}$'.format(self.plotting_dto.coefficients[0], self.plotting_dto.coefficients[1]),
            r'boards=%s' % ("\n              ".join(self.board_names))
        ))

    def save(self):
        ax = plt.subplot(111)
        chartBox = ax.get_position()

        ax.plot(self.plotting_dto.committed, self.plotting_dto.completed, 'ro', label="data points")
        ax.plot(self.plotting_dto.x_values, self.plotting_dto.y_values, '-', color="blue", label="trendline")
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
                         y1=self.plotting_dto.ciy_plus,
                         y2=self.ymax,
                         where=self.ymax > self.plotting_dto.ciy_plus,
                         facecolor="#DDDDDD",
                         interpolate=True)

        plt.fill_between(x=self.x_space,
                         y1=self.zeros,
                         y2=self.plotting_dto.ciy_minus,
                         where=self.plotting_dto.ciy_minus > self.zeros,
                         facecolor="#DDDDDD",
                         interpolate=True)

        plt.xlim((0, self.xlim))
        plt.ylim((0, self.ylim))
        plt.grid()
        plt.title(
            "Story point analysis with %s%% Confidence" % self.confidence_str)
        plt.xlabel('Committed Stories')
        plt.ylabel("Completed Stories")
        try:
            plt.savefig(self.filepath)
        except FileNotFoundError:
            self.filepath = os.pardir + '/static/images/plot_' + self.get_file_name()
            plt.savefig(self.filepath)

        plt.close('all')
        return os.path.abspath(self.filepath)

    def get_file_name(self):
        if len(self.board_names) != 0:
            names = [x.split()[0] for x in self.board_names]
            name_str = "-".join(names)
        else:
            name_str = "all"

        return name_str + "_" + self.confidence_str + "_" + self.now_string + ".png"
