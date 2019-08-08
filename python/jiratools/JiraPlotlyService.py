
class JiraPlotlyService:
    def __init__(self, jiraDataService):
        self.jiraDataService = jiraDataService

    def get_json(self):
        out = {}
        for x in self.jiraDataService.board_dict.keys():
            out[x] = self.jiraDataService.board_dict[x].to_json()
        return out
    '''
    {
        boardName: {
            committed: int[],
            completed: int[]
            names: string[],
                 
    '''