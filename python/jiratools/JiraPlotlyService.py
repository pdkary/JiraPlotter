import JiraAnalysisService


class JiraPlotlyService:
    def __init__(self, jiraDataService):
        self.jiraDataService = jiraDataService

    def get_json(self):
        out = {
            "analysis": JiraAnalysisService.analyze(self.jiraDataService.data_boards).to_json(),
            "boards" :{}
        }
        for x in self.jiraDataService.data_boards:
            out['boards'][x.name] = x.to_json()
        return out