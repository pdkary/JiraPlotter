from dtos.JiraAnalysisDto import JiraAnalysisBuilder
from dtos.JiraPlottingDto import JiraPlottingDto
import numpy as np


def get_analysis_dto(boards):
    committeds = [x.committed for x in boards]
    completeds = [x.completed for x in boards]
    committed = [x for l in committeds for x in l]
    completed = [x for l in completeds for x in l]
    coefficients, SSRes, rank, sing, rcond = np.polyfit(committed, completed, 1, full=True)

    n = len(completed)
    xbar = sum(committed) / n
    ybar = sum(completed) / n

    SSy = sum([(completed[i] - ybar) ** 2 for i in range(n)])
    SSx = sum([(committed[i] - xbar) ** 2 for i in range(n)])
    r_squared = 1 - SSRes / np.sqrt(SSy ** 2 + SSx ** 2)

    std_error_estimate = np.sqrt(
        (sum([(x - xbar) ** 2 for x in committed]) + sum(
            [(y - ybar) ** 2 for y in completed])) / (n - 1))

    return JiraAnalysisBuilder() \
        .set_committed(committed) \
        .set_completed(completed) \
        .set_coefficients(coefficients) \
        .set_r_squared(r_squared) \
        .set_ssx(SSx) \
        .set_ssy(SSy) \
        .set_ssr(SSRes) \
        .set_std_err(std_error_estimate) \
        .build()


def get_plotting_dto(boards):
    return JiraPlottingDto(get_analysis_dto(boards))
