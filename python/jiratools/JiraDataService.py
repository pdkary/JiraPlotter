import jira
import resources as rs
import re
from BoardData import BoardData
import time
import tqdm

jiraService = jira.JIRA(options=rs.options, basic_auth=(rs.user_name, rs.api_token))

jiraService.sprints

invalid_names = ["v2", "v3", "v4", "discovery", "feedback", "allprojects", "writing"]
d_pattern = re.compile("\w+D")
appos_pattern = re.compile("\w+'s")


def is_valid_board_name(board_name):
    if any(name in board_name.lower() for name in invalid_names) or d_pattern.match(board_name) or appos_pattern.match(
            board_name):
        return False
    return True


class JiraDataService:

    def __init__(self):
        self.all_boards = []
        self.filtered_boards = []
        self.data_boards = []
        self.get_boards()

    def get_all_boards(self):
        self.all_boards = jiraService.boards()
        return self.all_boards

    def get_filtered_boards(self):
        if len(self.all_boards) == 0:
            boards_to_filter = self.get_all_boards()
        else:
            boards_to_filter = self.all_boards
        return [x for x in boards_to_filter if is_valid_board_name(x.name)]

    def get_boards(self):
        if len(self.filtered_boards) == 0:
            boards_to_get = self.get_filtered_boards()
        else:
            boards_to_get = self.filtered_boards
        for x in tqdm.tqdm(boards_to_get):
            board = BoardData(x.name, x.id)
            board.prune()
            if not board.empty:
                self.data_boards += [board]
        return self.data_boards

    @property
    def board_dict(self):
        if len(self.data_boards) == 0:
            boards_to_dictify = self.get_boards()
        else:
            boards_to_dictify = self.data_boards
        return dict([(x.name, x) for x in boards_to_dictify])

    @property
    def names(self):
        return [x.name for x in self.data_boards]

    def get_by_names(self, name_list):
        return [self.board_dict[x] for x in name_list]


if __name__ == '__main__':
    start = time.time()
    j = JiraDataService()
    end = time.time()
    print("instantiation time: " + str(end - start))
    start2 = time.time()
    cd = j.get_by_names(["CV6 board", "DA board"])
    intb = j.get_by_names(["INT board"])
    end2 = time.time()
    print("get time: " + str(end2 - start2))
