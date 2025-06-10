from fastapi import FastAPI, HTTPException, Depends, Path, Query, Request
from typing import List, Optional, Type
from sqlmodel import Session, select
from sqlmodel import *
from typing import AsyncGenerator
import os
from dotenv import load_dotenv
from pydantic import ConfigDict
from db_connection import *
from sqlmodels_db import *
from models import *
from operations import *
from starlette.responses import JSONResponse
import pandas as pd
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import web
app = FastAPI()
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
app.include_router(web.router)
templates = Jinja2Templates(directory="templates/")



@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)



async def import_csv_data(session: AsyncSession, csv_file: str, model: Type[SQLModel]):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: El archivo CSV '{csv_file}' no se encontró.")
        return
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    for _, row in df.iterrows():
        try:
            # Crea un diccionario con los datos de la fila, manejando valores nulos y tipos
            row_dict = {col.lower(): value if pd.notnull(value) else None for col, value in row.items()}

            if model == GameSQL:
                # Ensure 'rank' is not None
                rank_value = row_dict.get('rank')
                if rank_value is None:
                    print(f"Skipping row with null 'Rank' value: {row_dict}")
                    continue  # Skip this row

                # Ensure 'review' is a string
                review_value = row_dict.get('review')
                if review_value is not None and not isinstance(review_value, str):
                    review_value = str(review_value)

                # Crea una instancia del modelo GameSQL
                game_instance = GameSQL(
                    Rank=rank_value,
                    Game_Title=row_dict.get('game_title'),
                    Platform=row_dict.get('platform'),
                    Year=row_dict.get('year'),
                    Genre=row_dict.get('genre'),
                    Publisher=row_dict.get('publisher'),
                    North_America=row_dict.get('north_america'),
                    Europe=row_dict.get('europe'),
                    Japan=row_dict.get('japan'),
                    Rest_of_World=row_dict.get('rest_of_world'),
                    Global=row_dict.get('global'),
                    Review=review_value  # Use the converted review_value
                )
                session.add(game_instance)
            elif model == ConsoleSQL:
                # Crea una instancia del modelo ConsoleSQL
                console_instance = ConsoleSQL(
                    Id=row_dict.get('id'),
                    Console_Name=row_dict.get('console_name'),
                    Type=row_dict.get('type'),
                    Company=row_dict.get('company'),
                    Released_Year=row_dict.get('released_year'),
                    Discontinuation_Year=row_dict.get('discontinuation_year'),
                    Units_Sold=row_dict.get('units_sold')
                )
                session.add(console_instance)
            else:
                print(f"Error: Modelo no soportado: {model.__name__}")
                return

        except Exception as e:
            print(f"Error al procesar la fila: {e}")
            await session.rollback()  # Rollback en caso de error en una fila
            continue  # Continuar con la siguiente fila

    await session.commit()
    print(f"Datos del archivo CSV '{csv_file}' importados a la tabla '{model.__tablename__}' exitosamente.")



@app.get("/import-data/")
async def import_data_endpoint(session: AsyncSession = Depends(get_session),):
    await import_csv_data(session, "data/games.csv", GameSQL)
    await import_csv_data(session, "data/consoles.csv", ConsoleSQL)
    return {"message": "Importación de datos iniciada y exitosa."}



@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@app.post("/games/", response_model=GameSQL, tags=["Create Game"])
async def create_game_endpoint(game: GameSQL, session: AsyncSession = Depends(get_session)):
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game

@app.get("/games/", response_model=List[GameSQL], tags=["List Games"])
async def list_games_endpoint(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(GameSQL))
    games = result.scalars().all()
    return games

@app.get("/games/{game_id}", response_model=GameSQL, tags=["Get Game"])
async def get_game_by_id_endpoint(game_id: int, session: AsyncSession = Depends(get_session)):
    game = await session.get(GameSQL, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.put("/games/{game_id}", response_model=GameSQL, tags=["Update Game"])
async def update_game_endpoint(game_id: int, updated_game: GameSQL, session: AsyncSession = Depends(get_session)):
    """
    Update a game by its ID.
    """
    db_game = await session.get(GameSQL, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Update attributes
    db_game.Game_Title = updated_game.Game_Title
    db_game.Platform = updated_game.Platform
    db_game.Year = updated_game.Year
    db_game.Genre = updated_game.Genre
    db_game.Publisher = updated_game.Publisher
    db_game.North_America = updated_game.North_America
    db_game.Europe = updated_game.Europe
    db_game.Japan = updated_game.Japan
    db_game.Rest_of_World = updated_game.Rest_of_World
    db_game.Global = updated_game.Global
    db_game.Review = updated_game.Review

    session.add(db_game)
    await session.commit()
    await session.refresh(db_game)
    return db_game

@app.delete("/games/{game_id}", response_model=GameSQL, tags=["Delete Game"])
async def delete_game_by_id_endpoint(game_id: int, session: AsyncSession = Depends(get_session)):
    game = await session.get(GameSQL, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    await session.delete(game)
    await session.commit()
    return game
@app.post("/consoles/", response_model=ConsoleSQL, tags=["Create Console"])
async def create_console_endpoint(console: ConsoleSQL, session: AsyncSession = Depends(get_session)):
    session.add(console)
    await session.commit()
    await session.refresh(console)
    return console


@app.get("/consoles/", response_model=List[ConsoleSQL], tags=["List Consoles"])
async def list_consoles_endpoint(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ConsoleSQL))
    consoles = result.scalars().all()
    return consoles



@app.get("/consoles/{console_id}", response_model=ConsoleSQL, tags=["Get Console"])
async def get_console_by_id_endpoint(console_id: int, session: AsyncSession = Depends(get_session)):
    console = await session.get(ConsoleSQL, console_id)
    if not console:
        raise HTTPException(status_code=404, detail="Consola no encontrada")
    return console



@app.put("/consoles/{console_id}", response_model=ConsoleSQL, tags=["Update Console"])
async def update_console_endpoint(console_id: int, updated_console: ConsoleSQL, session: AsyncSession = Depends(get_session)):
    db_console = await session.get(ConsoleSQL, console_id)
    if not db_console:
        raise HTTPException(status_code=404, detail="Consola no encontrada")

    db_console.Console_Name = updated_console.Console_Name
    db_console.Type = updated_console.Type
    db_console.Company = updated_console.Company
    db_console.Released_Year = updated_console.Released_Year
    db_console.Discontinuation_Year = updated_console.Discontinuation_Year
    db_console.Units_Sold = updated_console.Units_Sold

    session.add(db_console)
    await session.commit()
    await session.refresh(db_console)
    return db_console



@app.delete("/consoles/{console_id}", response_model=ConsoleSQL, tags=["Delete Console"])
async def delete_console_by_id_endpoint(console_id: int, session: AsyncSession = Depends(get_session)):
    console = await session.get(ConsoleSQL, console_id)
    if not console:
        raise HTTPException(status_code=404, detail="Consola no encontrada")
    await session.delete(console)
    await session.commit()
    return console


###CSV
app.get("/games-csv", response_model=List[GameWithId])
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