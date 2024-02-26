#!/usr/bin python3

import os
from tools.sheetsapi import SheetsAPI
from tools import tournamenttools

from rich import print
from rich.prompt import Prompt, Confirm

ELO_PATH = os.path.join(os.path.dirname(__file__), "Elo")

TYPE_LIBRARY = {
    "Canlander23": "Canlander Stats",
    "Canlander24": "Canlander Stats",
    "CanlanderEndless": "Canlander Stats",
}

YEAR_TYPE = {
    "Canlander23": "23",
    "Canlander24": "24",
}

if not os.path.exists(ELO_PATH):
    os.makedirs(ELO_PATH)
for key in TYPE_LIBRARY.keys():
    if not os.path.exists(os.path.join(ELO_PATH, key)):
        os.makedirs(os.path.join(ELO_PATH, key))

print("Welcome to the tournament manager!")

automatic = Confirm.ask("Do you want to run all tournaments automatically?")

types = []
if automatic:
    types = list(TYPE_LIBRARY.keys())
    all_events = True
else:
    types.append(
        Prompt.ask(
            "Which type of tournament do you want to run?",
            choices=TYPE_LIBRARY.keys()
        )
    )
    all_events = Confirm.ask(
        "Do you want to run all events of a specific type?"
        )

publish = Confirm.ask("Do you want to publish the results?")

for type in types:
    dates = []

    if all_events:
        all_dates = SheetsAPI(TYPE_LIBRARY[type]).fetch_all_tournamet_dates()
        for date in all_dates:
            if not os.path.exists(
                os.path.join(ELO_PATH, type, f"{date.replace('/', '_')}.json")
            ):
                if type in YEAR_TYPE:
                    if date[-2:] != YEAR_TYPE[type]:
                        continue
                dates.append(date)
    else:
        date = Prompt.ask("Which date do you want to run? (dd/mm/yyyy)")
        date_array = date.split("/")
        while (
            len(date_array) != 3
            or len(date_array[0]) != 2
            or len(date_array[1]) != 2
            or len(date_array[2]) != 4
        ):
            print(
                "[bold red]ERROR: The date has to be in the format \
                    dd/mm/yyyy[/bold red]"
            )
            date = Prompt.ask("Which date do you want to run? (dd/mm/yyyy)")
            date_array = date.split("/")
        # check if date ist newer than last tournament
        for file in os.listdir(os.path.join("Elo", type)):
            if file.endswith(".json"):
                if tournamenttools.dt.strptime(
                    file[:-5], "%d_%m_%Y"
                ) > tournamenttools.dt.strptime(date, "%d/%m/%Y"):
                    print(
                        f"[bold red]ERROR: The date {date} is not newer than \
                            the last tournament {file[:-5]}[/bold red]"
                    )
                    if not Confirm.ask("Do you want to continue?"):
                        exit()
        dates.append(date)

    if len(dates) == 0:
        print(
            f"[bold yellow]WARNING: No new tournaments of type {type} \
                found[/bold yellow]"
        )
        continue

    print("Processing tournaments for type", type, "and dates", dates, "...")
    tournament = None
    for date in dates:
        tournament = tournamenttools.process_tournament(
            type, date, sheetsName=TYPE_LIBRARY[type]
        )
    if publish and tournament is not None:
        print("Publishing results ...")
        tournament.publish()
print("Done!")
