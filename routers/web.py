from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form, HTTPException, FastAPI, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func
# from db_ops import parse_float # Esto no se usa en el snippet, puedes comentarlo o eliminarlo si no lo necesitas
from db_connection import get_session, AsyncSession
from typing import Optional
from sqlmodels_db import ConsoleSQL, GameSQL, ArchivedGameSQL, ArchivedConsoleSQL, Subscriber
import db_ops as crud  # Debe tener funciones para games y consoles

# app = FastAPI() # Esta línea debe estar en main.py, no aquí.
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ---------------- HOME & ABOUT PAGES ----------------
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# --- CORRECCIÓN: Unificamos y movemos la ruta /about para evitar duplicados ---
@router.get("/about", response_class=HTMLResponse)
async def about_project(request: Request, subscription_message: Optional[str] = None):
    """Muestra la página "Sobre el proyecto" y puede mostrar mensajes de suscripción."""
    return templates.TemplateResponse(
        "about.html",
        {"request": request, "subscription_message": subscription_message}
    )

@router.get("/about_me", response_class=HTMLResponse)
async def about_me_page(request: Request):
    """Displays the 'About Me' page."""
    return templates.TemplateResponse("about_me.html", {"request": request})


# ---------------- CONSOLES ----------------
@router.get("/consoles/view", response_class=HTMLResponse)
async def consoles_list(
    request: Request,
    page: int = 1,
    session: Session = Depends(get_session)
):
    limit = 10
    offset = (page - 1) * limit

    all_consoles = await crud.get_consoles(session)
    total_consoles = len(all_consoles)
    total_pages = (total_consoles + limit - 1) // limit

    consoles = all_consoles[offset : offset + limit]

    return templates.TemplateResponse("consoles/consoles.html", {
        "request": request,
        "consoles": consoles,
        "page": page,
        "total_pages": total_pages
    })

@router.get("/consoles/search", response_class=HTMLResponse)
async def search_consoles(
    request: Request,
    q: str = Query(...),
    session: Session = Depends(get_session)
):
    results = await crud.get_console_key(session, q)
    return templates.TemplateResponse("consoles/consoles.html", {
        "request": request,
        "consoles": results,
        "show_actions": True,
        "page": 1,
        "total_pages": 1
    })

# --- CORRECCIÓN CLAVE: La ruta GET va PRIMERO ---
@router.get("/consoles/create", response_class=HTMLResponse)
async def create_console_form(request: Request, error_message: Optional[str] = None): # Agregamos error_message
    return templates.TemplateResponse("consoles/create.html", {"request": request, "error_message": error_message})

@router.post("/consoles/create", response_class=RedirectResponse, status_code=303) # CORREGIDO: response_class y status_code
async def create_console_from_form(
    request: Request,
    session: AsyncSession = Depends(get_session),
    Console_Name: str = Form(...),
    Type: str = Form(...),
    Company: str = Form(...),
    Released_Year: int = Form(...),
    Discontinuation_Year: Optional[int] = Form(None),
    Units_Sold: Optional[float] = Form(None),
):
    try:
        new_console_db = ConsoleSQL(
            Console_Name=Console_Name,
            Type=Type,
            Company=Company,
            Released_Year=Released_Year,
            Discontinuation_Year=Discontinuation_Year,
            Units_Sold=Units_Sold
        )
        session.add(new_console_db)
        await session.commit()
        await session.refresh(new_console_db)
        return RedirectResponse(url="/consoles/view", status_code=303)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # CORREGIDO: Redirección con mensaje de error
        error_message = f"Error al crear la consola: {e}. Por favor, revisa los datos ingresados."
        return RedirectResponse(url=f"/consoles/create?error_message={error_message}", status_code=303)


# GET para mostrar el formulario de edición de una consola
@router.get("/consoles/{console_id}/edit", response_class=HTMLResponse)
async def edit_console_form(console_id: int, request: Request, session: AsyncSession = Depends(get_session), error_message: Optional[str] = None): # Agregamos error_message
    """Muestra el formulario para editar una consola existente."""
    console = await session.get(ConsoleSQL, console_id)
    if not console:
        raise HTTPException(status_code=404, detail="Console not found for editing.")
    return templates.TemplateResponse("consoles/edit_console.html", {"request": request, "console": console, "error_message": error_message})


# POST para procesar el envío del formulario de edición de una consola
@router.post("/consoles/{console_id}/edit", response_class=RedirectResponse, status_code=303) # CORREGIDO: response_class y status_code
async def update_console_from_form(
    console_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    Console_Name: str = Form(...),
    Type: str = Form(...),
    Company: str = Form(...),
    Released_Year: int = Form(...),
    Discontinuation_Year: Optional[int] = Form(None),
    Units_Sold: Optional[float] = Form(None)
):
    """Procesa los datos del formulario y actualiza una consola."""
    db_console = await session.get(ConsoleSQL, console_id)
    if not db_console:
        raise HTTPException(status_code=404, detail="Console not found for update.")

    try:
        db_console.Console_Name = Console_Name
        db_console.Type = Type
        db_console.Company = Company
        db_console.Released_Year = Released_Year
        db_console.Discontinuation_Year = Discontinuation_Year
        db_console.Units_Sold = Units_Sold

        session.add(db_console)
        await session.commit()
        await session.refresh(db_console)
        return RedirectResponse(url=f"/consoles/view", status_code=303)
    except Exception as e:
        print(f"Error updating console {console_id}: {e}")
        # CORREGIDO: Redirección con mensaje de error
        error_message = f"Error al actualizar la consola: {e}. Por favor, revisa los datos ingresados."
        return RedirectResponse(url=f"/consoles/{console_id}/edit?error_message={error_message}", status_code=303)


@router.post("/consoles/{console_id}/delete", response_class=RedirectResponse, status_code=303)
async def move_console_to_archive(console_id: int, session: AsyncSession = Depends(get_session)):
    """Mueve una consola a la tabla de consolas archivadas y la elimina de la tabla principal."""
    console_to_archive = await session.get(ConsoleSQL, console_id)
    if not console_to_archive:
        raise HTTPException(status_code=404, detail="Consola no encontrada para archivar.")

    archived_console = ArchivedConsoleSQL(
        id=console_to_archive.id,
        Console_Name=console_to_archive.Console_Name,
        Type=console_to_archive.Type,
        Company=console_to_archive.Company,
        Released_Year=console_to_archive.Released_Year,
        Discontinuation_Year=console_to_archive.Discontinuation_Year,
        Units_Sold=console_to_archive.Units_Sold,
        archived_at=datetime.now()
    )

    session.add(archived_console)
    await session.delete(console_to_archive)

    await session.commit()
    return RedirectResponse(url="/consoles/view", status_code=303)

@router.get("/consoles/archived", response_class=HTMLResponse)
async def view_archived_consoles(request: Request, session: AsyncSession = Depends(get_session)):
    """Muestra una lista de consolas archivadas."""
    archived_consoles_statement = select(ArchivedConsoleSQL)
    archived_consoles_result = await session.execute(archived_consoles_statement)
    archived_consoles = archived_consoles_result.scalars().all()
    return templates.TemplateResponse(
        "consoles/archived_consoles.html",
        {"request": request, "archived_consoles": archived_consoles}
    )

# ---------------- GAMES ----------------
@router.get("/games/view", response_class=HTMLResponse)
async def games_list(request: Request, session: Session = Depends(get_session), page: int = 1, per_page: int = 20):
    skip = (page - 1) * per_page
    games = await crud.get_games_paginated(session, skip=skip, limit=per_page)

    total_games = await session.exec(select(func.count()).select_from(GameSQL))
    total = total_games.one()

    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("/games/games.html", {
        "request": request,
        "games": games,
        "page": page,
        "total_pages": total_pages,
    })

@router.get("/games/search", response_class=HTMLResponse)
async def search_games(
    request: Request,
    q: str = "",
    page: int = 1,
    session: Session = Depends(get_session)
):
    PAGE_SIZE = 10
    all_results = await crud.get_game_key(session, q)
    total_results = len(all_results)
    total_pages = (total_results + PAGE_SIZE - 1) // PAGE_SIZE

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    paginated_results = all_results[start:end]

    return templates.TemplateResponse("games/games.html", {
        "request": request,
        "games": paginated_results,
        "page": page,
        "total_pages": total_pages,
        "query": q
    })

# --- CORRECCIÓN CLAVE: La ruta GET va PRIMERO ---
@router.get("/games/create", response_class=HTMLResponse)
async def create_game_form(request: Request, error_message: Optional[str] = None): # Agregamos error_message
    return templates.TemplateResponse("games/create.html", {"request": request, "error_message": error_message})

@router.post("/games/create", response_class=RedirectResponse, status_code=303) # CORREGIDO: response_class y status_code
async def create_game_from_form(
    request: Request,
    session: AsyncSession = Depends(get_session),
    Rank: int = Form(...),
    Game_Title: str = Form(...),
    Platform: str = Form(...),
    Year: int = Form(...),
    Genre: str = Form(...),
    Publisher: str = Form(...),
    North_America: Optional[float] = Form(None),
    Europe: Optional[float] = Form(None),
    Japan: Optional[float] = Form(None),
    Rest_of_World: Optional[float] = Form(None),
    Global: Optional[float] = Form(None),
    Review: Optional[str] = Form(None),
):
    try:
        new_game_db = GameSQL(
            Rank=Rank,
            Game_Title=Game_Title,
            Platform=Platform,
            Year=Year,
            Genre=Genre,
            Publisher=Publisher,
            North_America=North_America,
            Europe=Europe,
            Japan=Japan,
            Rest_of_World=Rest_of_World,
            Global=Global,
            Review=Review
        )
        session.add(new_game_db)
        await session.commit()
        await session.refresh(new_game_db)
        return RedirectResponse(url="/games/view", status_code=303)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # CORREGIDO: Redirección con mensaje de error
        error_message = f"Error al crear el juego: {e}. Por favor, revisa los datos ingresados."
        return RedirectResponse(url=f"/games/create?error_message={error_message}", status_code=303)


@router.get("/games/{game_id}/edit", response_class=HTMLResponse)
async def edit_game_form(game_id: int, request: Request, session: AsyncSession = Depends(get_session), error_message: Optional[str] = None): # Agregamos error_message
    """Muestra el formulario para editar un juego existente."""
    game = await session.get(GameSQL, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found for editing.")
    return templates.TemplateResponse("games/edit_game.html", {"request": request, "game": game, "error_message": error_message})

# POST para procesar el envío del formulario de edición de un juego
@router.post("/games/{game_id}/edit", response_class=RedirectResponse, status_code=303) # CORREGIDO: response_class y status_code
async def update_game_from_form(
    game_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    Rank: int = Form(...),
    Game_Title: str = Form(...),
    Platform: str = Form(...),
    Year: int = Form(...),
    Genre: str = Form(...),
    Publisher: str = Form(...),
    North_America: Optional[float] = Form(None),
    Europe: Optional[float] = Form(None),
    Japan: Optional[float] = Form(None),
    Rest_of_World: Optional[float] = Form(None),
    Global: Optional[float] = Form(None),
    Review: Optional[str] = Form(None)
):
    """Procesa los datos del formulario y actualiza un juego."""
    db_game = await session.get(GameSQL, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found for update.")

    try:
        db_game.Rank = Rank
        db_game.Game_Title = Game_Title
        db_game.Platform = Platform
        db_game.Year = Year
        db_game.Genre = Genre
        db_game.Publisher = Publisher
        db_game.North_America = North_America
        db_game.Europe = Europe
        db_game.Japan = Japan
        db_game.Rest_of_World = Rest_of_World
        db_game.Global = Global
        db_game.Review = Review

        session.add(db_game)
        await session.commit()
        await session.refresh(db_game)
        return RedirectResponse(url=f"/games/view", status_code=303)
    except Exception as e:
        print(f"Error updating game {game_id}: {e}")
        # CORREGIDO: Redirección con mensaje de error
        error_message = f"Error al actualizar el juego: {e}. Por favor, revisa los datos ingresados."
        return RedirectResponse(url=f"/games/{game_id}/edit?error_message={error_message}", status_code=303)


@router.post("/games/{game_id}/delete", response_class=RedirectResponse, status_code=303)
async def move_game_to_archive(game_id: int, session: AsyncSession = Depends(get_session)):
    """Mueve un juego a la tabla de juegos archivados y lo elimina de la tabla principal."""
    game_to_archive = await session.get(GameSQL, game_id)
    if not game_to_archive:
        raise HTTPException(status_code=404, detail="Juego no encontrado para archivar.")

    archived_game = ArchivedGameSQL(
        index=game_to_archive.index,
        Rank=game_to_archive.Rank,
        Game_Title=game_to_archive.Game_Title,
        Platform=game_to_archive.Platform,
        Year=game_to_archive.Year,
        Genre=game_to_archive.Genre,
        Publisher=game_to_archive.Publisher,
        North_America=game_to_archive.North_America,
        Europe=game_to_archive.Europe,
        Japan=game_to_archive.Japan,
        Rest_of_World=game_to_archive.Rest_of_World,
        Global=game_to_archive.Global,
        Review=game_to_archive.Review,
        archived_at=datetime.now()
    )

    session.add(archived_game)
    await session.delete(game_to_archive)

    await session.commit()
    return RedirectResponse(url="/games/view", status_code=303)

@router.get("/games/archived", response_class=HTMLResponse)
async def view_archived_games(request: Request, session: AsyncSession = Depends(get_session)):
    """Muestra una lista de juegos archivados."""
    archived_games_statement = select(ArchivedGameSQL)
    archived_games_result = await session.execute(archived_games_statement)
    archived_games = archived_games_result.scalars().all()
    return templates.TemplateResponse(
        "games/archived_games.html",
        {"request": request, "archived_games": archived_games}
    )


# ---------------- SUBSCRIPTIONS ----------------
@router.post("/subscribe", response_class=RedirectResponse, status_code=303)
async def subscribe_email(
    request: Request,
    email: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Procesa el formulario de suscripción de email."""
    message = ""
    try:
        if "@" not in email or "." not in email:
            message = "Formato de correo electrónico inválido."
            return RedirectResponse(url=f"/about?subscription_message={message}", status_code=303)

        existing_subscriber = await session.exec(select(Subscriber).where(Subscriber.email == email))
        if existing_subscriber.first():
            message = "Este correo electrónico ya está suscrito."
            return RedirectResponse(url=f"/about?subscription_message={message}", status_code=303)

        new_subscriber = Subscriber(email=email)
        session.add(new_subscriber)
        await session.commit()
        await session.refresh(new_subscriber)
        message = "¡Gracias por suscribirte exitosamente!"
        return RedirectResponse(url=f"/about?subscription_message={message}", status_code=303)

    except Exception as e:
        print(f"Error al suscribir el email {email}: {e}")
        message = f"Ocurrió un error al intentar suscribirte: {e}"
        return RedirectResponse(url=f"/about?subscription_message={message}", status_code=303)

@router.get("/subscribers", response_class=HTMLResponse)
async def view_subscribers(request: Request, session: AsyncSession = Depends(get_session)):
    """Muestra una lista de todos los suscriptores."""
    subscribers_statement = select(Subscriber)
    subscribers_result = await session.execute(subscribers_statement)
    subscribers = subscribers_result.scalars().all()
    return templates.TemplateResponse(
        "subscribers.html",
        {"request": request, "subscribers": subscribers}
    )