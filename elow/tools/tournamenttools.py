import json
import os

from .tournament import Tournament
from datetime import datetime as dt

MAIN_DIRECTORY = os.path.join(os.path.dirname(__file__), "Elo")

def process_tournament(tournamentType, date, sheetsName="Canlander Stats"):
    tournament = create_tournament(tournamentType, date, sheetsName=sheetsName)
    tournament.run_tournament()
    tournament.calculate_results()
    save_json(tournament)
    return tournament

def create_tournament(tournamentType, date, sheetsName="Canlander Stats"):
    tournament_before = load_json_before(tournamentType, date)
    if tournament_before is None:
        return Tournament(date, sheetsName=sheetsName, eloSheetName=tournamentType)
    return Tournament(date, playerlist=tournament_before.players, sheetsName=sheetsName, eloSheetName=tournamentType)
    
def save_json(tournament: Tournament) -> dict:
    playerlist = get_json(tournament)
    filename = f"{tournament.date.replace('/', '_')}.json"
    with open(os.path.join(MAIN_DIRECTORY, tournament.elo_sheet_name, filename), "w") as f:
        json.dump(playerlist, f, indent=2, ensure_ascii=False)
    return playerlist

def get_json(tournament: Tournament) -> dict:
    playerlist = {}
    playerlist["list"] = tournament.players
    playerlist["sheetsName"] = tournament.sheets_name
    playerlist["eloSheetName"] = tournament.elo_sheet_name
    return playerlist

def load_json(tournamentType, date) -> Tournament:
    filename = f"{date.replace('/', '_')}.json"
    with open(os.path.join(MAIN_DIRECTORY, tournamentType, filename)) as f:
        playerlist = json.load(f)
    return Tournament(date, playerlist=playerlist["list"], sheetsName=playerlist["sheetsName"], eloSheetName=playerlist["eloSheetName"])

def load_json_before(tournamentType, date) -> Tournament:
    date_before = find_last_tournament(tournamentType, date)
    if date_before is None:
        return None
    return load_json(tournamentType, date_before)

def find_last_tournament(tournamentType, date) -> str:
    date_before = "31_12_1999"
    for file in os.listdir(os.path.join(MAIN_DIRECTORY, tournamentType)):
        if file.endswith(".json"):
            if dt.strptime(file[:-5], "%d_%m_%Y") < dt.strptime(date, "%d/%m/%Y"):
                if dt.strptime(file[:-5], "%d_%m_%Y") > dt.strptime(date_before, "%d_%m_%Y"):
                    date_before = file[:-5]
    if date_before == "31_12_1999":
        return None
    return date_before
    