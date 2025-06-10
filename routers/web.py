from select import select

from fastapi import APIRouter, Request, Depends, Form, HTTPException, FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func

from db_connection import get_session
from sqlmodels_db import ConsoleSQL, GameSQL
import db_ops as crud  # Debe tener funciones para games y consoles
app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ---------------- HOME ----------------
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# ---------------- CONSOLES ----------------
@router.get("/consoles/view", response_class=HTMLResponse)
async def consoles_list(
    request: Request,
    page: int = 1,
    session: Session = Depends(get_session)
):
    limit = 10  # o el número que prefieras por página
    offset = (page - 1) * limit

    all_consoles = await crud.get_consoles(session)
    total_consoles = len(all_consoles)
    total_pages = (total_consoles + limit - 1) // limit  # redondeo hacia arriba

    consoles = all_consoles[offset : offset + limit]

    return templates.TemplateResponse("consoles/consoles.html", {
        "request": request,
        "consoles": consoles,
        "page": page,
        "total_pages": total_pages
    })

@router.get("/consoles/{console_id}", response_class=HTMLResponse)
async def one_console(request: Request, console_id: int, session: Session = Depends(get_session)):
    console = await crud.get_console(session, console_id)
    if console is None:
        raise HTTPException(status_code=404, detail="Console not found")
    return templates.TemplateResponse("includes/console_card.html", {
        "request": request,
        "console": console,
        "show_actions": True
    })


@router.get("/consoles/{console_id}/edit", response_class=HTMLResponse)
async def edit_console(request: Request, console_id: int, session: Session = Depends(get_session)):
    console = await crud.update_console(session, console_id)
    if console is None:
        raise HTTPException(status_code=404, detail="Console not found")
    return templates.TemplateResponse("consoles/edit.html", {
        "request": request,
        "console": console
    })


@router.post("/consoles/{console_id}/edit", response_class=HTMLResponse)
async def update_console(
    request: Request,
    console_id: int,
    name: str = Form(...),
    type: str = Form(...),
    company: str = Form(...),
    released_year: int = Form(...),
    discontinuation_year: int = Form(None),
    units_sold: float = Form(...),
    session: Session = Depends(get_session)
):
    updated_data = {
        "Console_Name": name,
        "Type": type,
        "Company": company,
        "Released_Year": released_year,
        "Discontinuation_Year": discontinuation_year,
        "Units_Sold": units_sold
    }
    await crud.update_console(session, console_id, updated_data)
    return RedirectResponse(f"/web/consoles/{console_id}", status_code=303)


@router.get("/consoles/{console_id}/delete", response_class=HTMLResponse)
async def delete_console(request: Request, console_id: int, session: Session = Depends(get_session)):
    await crud.delete_console(session, console_id)
    return RedirectResponse("/web/consoles", status_code=303)

# ---------------- GAMES ----------------
@router.get("/games/view", response_class=HTMLResponse)
async def games_list(request: Request, session: Session = Depends(get_session), page: int = 1, per_page: int = 20):
    skip = (page - 1) * per_page
    games = await crud.get_games_paginated(session, skip=skip, limit=per_page)

    # Calcular el total para saber cuántas páginas mostrar (opcional si tienes muchos juegos)
    total_games = await session.exec(select(func.count()).select_from(GameSQL))
    total = total_games.one()

    total_pages = (total + per_page - 1) // per_page  # Redondear hacia arriba

    return templates.TemplateResponse("/games/games.html", {
        "request": request,
        "games": games,
        "page": page,
        "total_pages": total_pages,
    })


@router.get("/games/{game_id}", response_class=HTMLResponse)
async def one_game(request: Request, game_id: int, session: Session = Depends(get_session)):
    game = await crud.get_game(session, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return templates.TemplateResponse("games/detail.html", {
        "request": request,
        "game": game,
        "show_actions": True
    })


@router.get("/games/{game_id}/edit", response_class=HTMLResponse)
async def edit_game(request: Request, game_id: int, session: Session = Depends(get_session)):
    game = await crud.get_game(session, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return templates.TemplateResponse("games/edit.html", {
        "request": request,
        "game": game
    })


@router.post("/games/{game_id}/edit", response_class=HTMLResponse)
async def update_game(
    request: Request,
    game_id: int,
    title: str = Form(...),
    platform: str = Form(...),
    year: int = Form(...),
    genre: str = Form(...),
    publisher: str = Form(...),
    session: Session = Depends(get_session)
):
    updated_data = {
        "Game_Title": title,
        "Platform": platform,
        "Year": year,
        "Genre": genre,
        "Publisher": publisher
    }
    await crud.update_game(session, game_id, updated_data)
    return RedirectResponse(f"/web/games/{game_id}", status_code=303)


@router.get("/games/{game_id}/delete", response_class=HTMLResponse)
async def delete_game(request: Request, game_id: int, session: Session = Depends(get_session)):
    await crud.delete_game(session, game_id)
    return RedirectResponse("/web/games", status_code=303)