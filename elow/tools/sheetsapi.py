import datetime
import gspread
import os


class SheetsAPI:

    def __init__(self, sheetsName = "Canlander Stats"):
        self.sheets_name = sheetsName
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        sa = gspread.service_account(filename=credentials_path)
        self.sheets_name = sheetsName
        self.sheets = sa.open(sheetsName)
        self.matches_worksheet = self.sheets.worksheet("Matches")
        try:
            self.decklist_links_sheet = self.sheets.worksheet("Decklist")
        except:
            self.decklist_links_sheet = None
    
    def update_elo_history(self, date, elo_dict):
        history = self.sheets.worksheet(elo_dict["eloSheetName"] + "History")
        dates = history.row_values(1)
        if date in dates: return
        column = len(dates) + 1
        history.update_cell(1, column, date)
        name_col = history.col_values(1)[1:]
        elo_col = history.col_values(column - 1)[1:]
        for player in elo_dict["list"].keys():
            if player not in name_col:
                name_col.append(player)
                elo_col.append(elo_dict["list"][player]["elo"])
            else:
                elo_col[name_col.index(player)] = elo_dict["list"][player]["elo"]
        history.update(gspread.utils.rowcol_to_a1(2, 1) + ":" + gspread.utils.rowcol_to_a1(len(name_col) + 1, 1), [[x] for x in name_col])
        history.update(gspread.utils.rowcol_to_a1(2, column) + ":" + gspread.utils.rowcol_to_a1(len(name_col) + 1, column), [[x] for x in elo_col])
    
    def fetch_all_tournamet_dates(self):
        return (sorted(list(set(self.matches_worksheet.col_values(1)[1:])), key=lambda x: datetime.datetime.strptime(x, '%d/%m/%Y')))
    
    def fetch_games_from_tournament(self, date):
        all_matches = self.matches_worksheet.get_all_values()
        games = []
        for row in all_matches:
            if row[0] == date:
                game = {}
                game["date"] = row[0]
                game["player1"] = row[1]
                game["player1_score"] = int(row[2])
                game["player2"] = row[4]
                game["player2_score"] = int(row[3])
                games.append(game)
        return games

    def fetch_decklist_links(self, playerlist):
        all_lists = self.decklist_links_sheet.get_all_values()
        decklistlist = {}
        for player in playerlist:
            for row in all_lists:
                if row[1] == player:
                    decklistlist[player] = row[2]
                    break
        return decklistlist
    
    def fetch_players_in_tournament(self, date):
        players = []
        all_matches = self.matches_worksheet.get_all_values()
        for row in all_matches:
            if row[0] == date:
                players.append(row[1])
                players.append(row[4])
        players = list(set(players))
        return players
    
    def fetch_all_players_in_last_tournament(self):
        all_dates = self.fetch_all_tournamet_dates()
        last_date = all_dates[-1]
        return self.fetch_players_in_tournament(last_date)
        