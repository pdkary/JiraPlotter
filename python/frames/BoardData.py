from frames.SprintData import SprintData


class BoardData(SprintData):
    def __init__(self, name, board_id):
        super().__init__(board_id)
        self.name = name
        self.board_id = board_id
