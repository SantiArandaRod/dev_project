from dataclasses import field

from pydantic import BaseModel, Field
from typing import Optional

class Game(BaseModel):
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

class GameWithId(Game):
    index: int
class GameResponse(BaseModel):
    id: int
    name: str
    console:str

class UpdatedGame(BaseModel):
    Rank: Optional[int]
    Game_Title: Optional[str]
    Platform: Optional[str]
    Year: Optional[int]
    Genre: Optional[str]
    Publisher: Optional[str]
    North_America: Optional[float]
    Europe: Optional[float]
    Japan: Optional[float]
    Rest_of_World: Optional[float]
    Global: Optional[float]
    Review: Optional[str]

class Console(BaseModel):
    Id: Optional[int] = Field(..., gt=-1)
    Console_Name:str = Field(..., min_length=1, max_length=50)
    Type:str = Field(..., min_length=1, max_length=50)
    Company:str = Field(..., min_length=1, max_length=50)
    Released_Year:int = Field(..., gt=-1, lt=2030)
    Discontinuation_Year:Optional[int] = Field(..., gt=-1, lt=2030)
    Units_Sold:float = Field(..., gt=-1)

class ConsoleWithId(Console):
    Id: int

class ConsoleResponse(Console):
    Id:int
    Console_Name:str
    Type:str
class UpdatedConsole(BaseModel):
    Id: Optional[int]
    Console_Name: Optional[str]
    Type: Optional[str]
    Company: Optional[str]
    Released_Year: Optional[int]
    Discontinuation_Year: Optional[int]
    Units_Sold: Optional[int]
