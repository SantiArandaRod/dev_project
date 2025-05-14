from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from sqlmodels_db import ConsoleSQL, GameSQL


async def create_console_sql(session: AsyncSession, console: ConsoleSQL) -> ConsoleSQL:
    """Create a new console."""
    db_console = console
    session.add(db_console)
    await session.commit()
    await session.refresh(db_console)
    return db_console


async def get_console(session: AsyncSession, console_id: int) -> Optional[ConsoleSQL]:
    """Get a console by ID."""
    return await session.get(ConsoleSQL, console_id)


async def get_consoles(session: AsyncSession) -> List[ConsoleSQL]:
    """Get all consoles."""
    result = await session.execute(select(ConsoleSQL))
    consoles = result.scalars().all()
    return consoles



async def update_console(session: AsyncSession, console_id: int, console_update: Dict[str, Any]) -> ConsoleSQL:
    """Update a console by ID."""
    db_console = await session.get(ConsoleSQL, console_id)
    if not db_console:
        raise HTTPException(status_code=404, detail="Console not found") #changed
    for key, value in console_update.items():
        if value is not None:
            setattr(db_console, key, value)
    session.add(db_console)
    await session.commit()
    await session.refresh(db_console)
    return db_console



async def create_game_sql(session: AsyncSession, game: GameSQL) -> GameSQL:
    """Create a new game."""
    db_game = game
    session.add(db_game)
    await session.commit()
    await session.refresh(db_game)
    return db_game


async def get_game(session: AsyncSession, game_id: int) -> Optional[GameSQL]:
    """Get a game by ID."""
    return await session.get(GameSQL, game_id)



async def get_games(session: AsyncSession) -> List[GameSQL]:
    """Get all games."""
    query = select(GameSQL)
    result = await session.execute(query)
    games = result.scalars().all()
    return games



async def update_gamee(session: AsyncSession, game_id: int, game_update: Dict[str, Any]) -> GameSQL:
    """Update a game by ID."""
    db_game = await session.get(GameSQL, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found") # changed

    for key, value in game_update.items():
        if value is not None:
            setattr(db_game, key, value)
    session.add(db_game)
    await session.commit()
    await session.refresh(db_game)
    return db_game
