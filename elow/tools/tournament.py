import gspread
import copy
import os
import time


class Tournament:
    def __init__(
        self,
        date,
        playerlist=None,
        sheetsName="Canlander Stats",
        eloSheetName="CanlanderEndless",
    ):
        self.date = date
        if playerlist is None:
            self.players = {}
            self.players_before = {}
        else:
            self.players = playerlist
            self.players_before = copy.deepcopy(playerlist)
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        sa = gspread.service_account(filename=credentials_path)
        self.sheets_name = sheetsName
        sh = sa.open(sheetsName)
        self.matches_worksheet = sh.worksheet("Matches")
        self.elo_sheet_name = eloSheetName
        self.elo_worksheet = sh.worksheet(eloSheetName)
        self.matches = self.__fetchMatches()
        self.tournamentfinished = False
        self.resultscalculated = False

    def run_tournament(self):
        if self.tournamentfinished:
            return
        playersInEvent = set()
        for m in self.matches:
            # Create players if they don't exist
            if m[0] not in self.players:
                self.players[m[0]] = {"elo": 1000, "playedEvents": 0}
            if m[3] not in self.players:
                self.players[m[3]] = {"elo": 1000, "playedEvents": 0}
            # Add players to set
            playersInEvent.add(m[0])
            playersInEvent.add(m[3])
            # Calculate elo
            player_1 = self.players[m[0]]["elo"]
            player_2 = self.players[m[3]]["elo"]
            if m[1] == m[2]:
                player_1, player_2 = Tournament.calc_elo([player_1, player_2], False)
            elif m[1] > m[2]:
                player_1, player_2 = Tournament.calc_elo([player_1, player_2], True)
            else:
                player_2, player_1 = Tournament.calc_elo([player_2, player_1], True)
            self.players[m[0]]["elo"] = round(player_1, 2)
            self.players[m[3]]["elo"] = round(player_2, 2)
        # Calculate played events
        for player in playersInEvent:
            self.players[player]["playedEvents"] += 1
        self.tournamentfinished = True
        return self

    def calculate_results(self):
        if self.resultscalculated:
            return
        # Calculate positions
        self.players = Tournament.calc_pos(self.players)
        # Calculate top 8
        for player in self.players.values():
            if player["position"] <= 8:
                player["top_eight"] = True
            else:
                player["top_eight"] = False
        # Calculate trends
        for player in self.players:
            if player not in self.players_before:
                self.players[player]["elo_trend"] = 0.00
                self.players[player]["position_trend"] = 0
                continue
            self.players[player]["elo_trend"] = round(
                self.players[player]["elo"] - self.players_before[player]["elo"], 2
            )
            self.players[player]["position_trend"] = round(
                self.players[player]["position"]
                - self.players_before[player]["position"],
                2,
            )
        # Calculate top 8 count
        for player in self.players:
            if "top_eight_count" not in self.players[player]:
                self.players[player]["top_eight_count"] = 0
            if self.players[player]["top_eight"]:
                self.players[player]["top_eight_count"] = (
                    self.players[player]["top_eight_count"] + 1
                )
        self.resultscalculated = True
        return self

    def publish(self):
        table = []
        for player in self.players:
            if self.players[player]["elo_trend"] < 0:
                elo_trend = str(abs(self.players[player]["elo_trend"])) + "↓"
            elif self.players[player]["elo_trend"] > 0:
                elo_trend = str(abs(self.players[player]["elo_trend"])) + "↑"
            else:
                elo_trend = "0"
            if self.players[player]["position_trend"] > 0:
                position_trend = str(abs(self.players[player]["position_trend"])) + "↓"
            elif self.players[player]["position_trend"] < 0:
                position_trend = str(abs(self.players[player]["position_trend"])) + "↑"
            else:
                position_trend = "0"
            table.append(
                [
                    self.players[player]["elo"],
                    self.__shortName(player),
                    elo_trend,
                    position_trend,
                    self.players[player]["playedEvents"],
                    self.players[player]["top_eight_count"],
                    player,
                ]
            )
        self.elo_worksheet.update("A1", table)

    def __shortName(self, name):
        array_name = name.split(" ")
        if len(array_name) > 1:
            return array_name[0] + " " + array_name[1][0] + "."
        else:
            return name

    def __fetchMatches(self):
        time.sleep(5)
        matches = self.matches_worksheet.get_all_values()
        matches_from_date = [match[1:] for match in matches if match[0] == self.date]
        return matches_from_date

    def calc_elo(elo, win=True):
        expected_player_1 = 1 / (1 + 10 ** ((elo[1] - elo[0]) / 400))
        expected_player_2 = 1 / (1 + 10 ** ((elo[0] - elo[1]) / 400))
        k_factor = 20
        if win:
            elo[0] += k_factor * (1 - expected_player_1)
            elo[1] += k_factor * (0 - expected_player_2)
        else:
            elo[0] += k_factor * (0.5 - expected_player_1)
            elo[1] += k_factor * (0.5 - expected_player_2)
        return elo

    def calc_pos(elo_dict):
        sorted_elo_list = sorted(
            elo_dict.items(), key=lambda x: x[1]["elo"], reverse=True
        )
        for i in range(len(sorted_elo_list)):
            elo_dict[sorted_elo_list[i][0]]["position"] = i + 1
        return elo_dict
