import sqlite3

from pydantic import ConfigDict
from sqlmodel import SQLModel
from sqlmodel import Field
from typing import Optional

class GameBase(SQLModel):
    Rank: int = Field(..., gt=-1)
    Game_Title: str = Field(..., min_length=1, max_length=500)
    Platform: str = Field(..., min_length=1, max_length=50)
    Year: Optional[float] = Field(..., gt=-1, lt=2030)
    Genre: str = Field(..., min_length=1, max_length=500)
    Publisher: str = Field(..., min_length=1, max_length=500)
    North_America: float = Field(..., ge=-1)
    Europe: float = Field(..., ge=-1)
    Japan: float = Field(..., ge=-1)
    Rest_of_World: float = Field(..., ge=-1)
    Global: float = Field(..., ge=-1)
    Review: str = Field(..., min_length=1, max_length=100)

class GameSQL(GameBase, table=True):
    __tablename__ = "games"
    id: Optional[int] = Field(default=None, primary_key=True)
    model_config = ConfigDict(from_attributes=True)

class ConsoleBase(SQLModel):
    Id: Optional[int] = Field(..., gt=-1)
    Console_Name: str = Field(..., min_length=1, max_length=50)
    Type: str = Field(..., min_length=1, max_length=50)
    Company: str = Field(..., min_length=1, max_length=50)
    Released_Year: int = Field(..., gt=-1, lt=2030)
    Discontinuation_Year: Optional[int] = Field(..., gt=-1, lt=2030)
    Units_Sold: float = Field(..., gt=-1)

class ConsoleSQL(ConsoleBase, table=True):
    __tablename__ = "consoles"
    id: Optional[int] = Field(default=None, primary_key=True)
    model_config = ConfigDict(from_attributes=True)