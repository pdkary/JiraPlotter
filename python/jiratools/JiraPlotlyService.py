import JiraAnalysisService


class JiraPlotlyService:
    def __init__(self, jiraDataService):
        self.jiraDataService = jiraDataService

    def get_json(self):
        out = {"anaysis": JiraAnalysisService.analyze(self.jiraDataService.data_boards).to_json()}
        for x in self.jiraDataService.data_boards:
            out[x.name] = x.to_json()
        return out