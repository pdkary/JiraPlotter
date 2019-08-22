from services import JiraAnalysisService


class JiraPlotlyService:
    def __init__(self, boards):
        self.boards = boards

    def get_json(self):
        out = {
            "analysis": JiraAnalysisService.get_analysis_dto(self.boards).to_json(),
            "boards": {}
        }
        for x in self.boards:
            out['boards'][x.name] = x.to_json()
        return out
