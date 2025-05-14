import csv
from db_connection import engine
from models import *

DATABASE_FILENAME = "data/games.csv"
DATABASE_FILENAME_CONSOLES = "data/consoles.csv"
column_fields = ["index", "Rank", "Game_Title", "Platform", "Year", "Genre", "Publisher", "North_America", "Europe", "Japan", "Rest_of_World","Global","Review"]
column_fields_consoles = ["Id", "Console_Name","Type","Company","Released_Year", "Discontinuation_Year","Units_Sold"]
def read_all_games():
    with open(DATABASE_FILENAME) as csvfile:
        reader = csv.DictReader(
            csvfile,
        )
        return [GameWithId(**row) for row in reader]

def read_one_game(game_id):
    with open(DATABASE_FILENAME) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row["index"]) == game_id:
                return GameWithId(**row)

def get_next_id():
    try:
        with open(DATABASE_FILENAME, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            max_id = max(int(row["index"]) for row in reader)
            return max_id + 1
    except:
        return 1

def write_game(game: GameWithId):
    with open(DATABASE_FILENAME, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=column_fields)
        writer.writerow(game.model_dump())

def new_game(game: Game):
    new_id = get_next_id()
    data = game.model_dump()
    data["index"] = new_id
    game_with_id = GameWithId(**data)
    write_game(game_with_id)
    return game_with_id

def modify_game(id: int, data: dict):
    games = read_all_games()
    updated = None

    for i, g in enumerate(games):
        if g.index == id:
            for key, value in data.items():
                setattr(g, key, value)
            updated = g
            break

    if updated:
        with open(DATABASE_FILENAME, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_fields)
            writer.writeheader()
            for game in games:
                writer.writerow(game.model_dump())
        return updated
    return None

def delete_game(id: int):
    games = read_all_games()
    deleted = None
    with open(DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=column_fields,
        )
        writer.writeheader()
        for game in games:
            if game.index == id:
                deleted = game
                # Backup the deleted game
                backup_deleted_game(deleted)
                continue
            writer.writerow(game.model_dump())
    if deleted:
        return deleted
def backup_deleted_game(game: GameWithId):
    with open("deleted_games.csv", mode="a", newline="") as backup_file:
        writer = csv.DictWriter(backup_file, fieldnames=column_fields)
        # Write the deleted game to the backup file
        writer.writerow(game.model_dump())

def read_all_consoles():
    with open(DATABASE_FILENAME_CONSOLES) as csvfile:
        reader = csv.DictReader(csvfile)
        return [ConsoleWithId(**{str(key): value for key, value in row.items()}) for row in reader]



def read_one_console(console_id):
    with open(DATABASE_FILENAME_CONSOLES) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row["Id"]) == console_id:
                return ConsoleWithId(**row)
def get_next_id_console():
    try:
        with open(DATABASE_FILENAME_CONSOLES, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            next_id= max(int(row["Id"]) for row in reader)
            return next_id + 1
    except:
        return 1

def write_console(console: ConsoleWithId):
    with open(DATABASE_FILENAME_CONSOLES, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=column_fields_consoles)
        writer.writerow(console.model_dump())
def new_console(console: Console):
    new_id = get_next_id_console()
    data = console.model_dump()
    data["Id"] = new_id
    console_with_id = ConsoleWithId(**data)
    write_console(console_with_id)
    return console_with_id
def modify_console(id: int, data: dict):
    consoles = read_all_consoles()
    updated = None
    for i, g in enumerate(consoles):
        if g.Id == id:
            for key, value in data.items():
                setattr(g, key, value)
            updated = g
            break

    if updated:
        with open(DATABASE_FILENAME_CONSOLES, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_fields_consoles)
            writer.writeheader()
            for console in consoles:
                writer.writerow(console.model_dump())
        return updated
    return None
def delete_console(id: int):
    consoles = read_all_consoles()
    deleted = None
    with open(DATABASE_FILENAME_CONSOLES, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=column_fields_consoles,
        )
        writer.writeheader()
        for console in consoles:
            if console.Id == id:
                deleted = console
                # Backup the deleted console
                backup_deleted_console(deleted)
                continue
            writer.writerow(console.model_dump())
    if deleted:
        return deleted

def backup_deleted_console(console: Console):
    with open("deleted_consoles.csv", mode="a", newline="") as backup_file:
        writer = csv.DictWriter(backup_file, fieldnames=column_fields_consoles)
        # Write the deleted console to the backup file
        writer.writerow(console.model_dump())