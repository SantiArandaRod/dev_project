from fastapi import FastAPI, HTTPException, Query
from starlette.responses import JSONResponse
from typing import List, Optional
from models import *
from operations import *

app = FastAPI()


@app.get("/")
def home():
    return {"message": "so far so good!"}


@app.get("/games", response_model=List[GameWithId])
async def show_all_games(
        title: Optional[str] = Query(None),
        genre: Optional[str] = Query(None),
        platform: Optional[str] = Query(None)
):
    games = read_all_games()

    if title:
        games = [game for game in games if game.Game_Title.lower() == title.lower()]
    if genre:
        games = [game for game in games if game.Genre.lower() == genre.lower()]
    if platform:
        games = [game for game in games if game.Platform.lower() == platform.lower()]

    return games


@app.get("/game/{game_id}", response_model=GameWithId)
async def show_game(game_id: int):
    game = read_one_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@app.post("/game", response_model=GameWithId)
async def add_game(game: Game):
    existing_game = read_one_game(game.Rank)  # Asumiendo que Rank es único
    if existing_game:
        raise HTTPException(status_code=409, detail="Game with this Rank already exists")

    return new_game(game)


@app.put("/game/{game_id}", response_model=GameWithId)
async def update_game(game_id: int, update_game: UpdatedGame):
    modified = modify_game(
        game_id, update_game.model_dump(exclude_unset=True),
    )
    if not modified:
        raise HTTPException(status_code=404, detail="Game not found or not updated")
    return modified


@app.delete("/game/{game_id}", response_model=Game)
async def delete_game_by_id(game_id: int):
    deleted = delete_game(game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Game not found or not deleted")
    return deleted


@app.get("/consoles", response_model=List[ConsoleWithId])
async def show_all_consoles(
        Console_Name: Optional[str] = Query(None),
        Released_Year: Optional[int] = Query(None),
        Units_Sold: Optional[float] = Query(None),
        Company: Optional[str] = Query(None)
):
    consoles = read_all_consoles()

    if Company:
        consoles = [console for console in consoles if console.Company.lower() == Company.lower()]
    if Console_Name:
        consoles = [console for console in consoles if console.Console_Name.lower() == Console_Name.lower()]
    if Released_Year:
        consoles = [console for console in consoles if console.Released_Year == Released_Year]
    if Units_Sold is not None:
        consoles = [console for console in consoles if console.Units_Sold == Units_Sold]

    return consoles


@app.get("/console/{console_id}", response_model=ConsoleWithId)
async def show_console(console_id: int):
    console = read_one_console(console_id)
    if not console:
        raise HTTPException(status_code=404, detail="Console not found")
    return console


@app.post("/console", response_model=ConsoleWithId)
async def add_console(console: Console):
    existing_console = read_one_console(console.Id)  # Asumiendo que Id es único
    if existing_console:
        raise HTTPException(status_code=409, detail="Console with this Id already exists")

    return new_console(console)


@app.put("/console/{console_id}", response_model=ConsoleWithId)
async def update_console(console_id: int, update_console: UpdatedConsole):
    modified = modify_console(
        console_id, update_console.model_dump(exclude_unset=True),
    )
    if not modified:
        raise HTTPException(status_code=404, detail="Console not found or not updated")
    return modified


@app.delete("/console/{console_id}", response_model=Console)
async def delete_console_by_id(console_id: int):
    deleted = delete_console(console_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Console not found or not deleted")
    return deleted


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": "Something is wrong",
            "detail": exc.detail,
            "path": str(request.url)
        },
    )