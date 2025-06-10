import sqlite3
from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel
from sqlmodel import Field
from typing import Optional

class GameBase(SQLModel):
    Rank: int = Field(..., gt=-1)
    Game_Title: str = Field(..., min_length=1, max_length=500)
    Platform: str = Field(..., min_length=1, max_length=50)
    Year: Optional[int] = Field(..., gt=-1, lt=2030)
    Genre: str = Field(..., min_length=1, max_length=500)
    Publisher: str = Field(..., min_length=1, max_length=500)
    North_America: Optional[float] = Field(default=None, ge=-1)  # Made default=None to be truly optional
    Europe: Optional[float] = Field(default=None, ge=-1)
    Japan: Optional[float] = Field(default=None, ge=-1)
    Rest_of_World: Optional[float] = Field(default=None, ge=-1)
    Global: Optional[float] = Field(default=None, ge=-1)
    Review: Optional[str] = Field(default=None, max_length=100)

class GameSQL(GameBase, table=True):
    __tablename__ = "games"
    index: Optional[int] = Field(default=None, primary_key=True)
    model_config = ConfigDict(from_attributes=True)

class ConsoleBase(SQLModel):
    Console_Name: str = Field(..., min_length=1, max_length=50)
    Type: str = Field(..., min_length=1, max_length=50)
    Company: str = Field(..., min_length=1, max_length=50)
    Released_Year: int = Field(..., gt=-1, lt=2030)
    Discontinuation_Year: Optional[int] = Field(default=None, gt=-1, lt=2030)
    Units_Sold: Optional[float] = Field(default=None, gt=-1)

class ConsoleSQL(ConsoleBase, table=True):
    __tablename__ = "consoles"
    id: Optional[int] = Field(default=None, primary_key=True)
    model_config = ConfigDict(from_attributes=True)


    ####Updated Models
class GameUpdate(SQLModel):
        # Todos los campos son opcionales y pueden ser None si no se proporcionan
        Rank: Optional[int] = Field(default=None, gt=-1)
        Game_Title: Optional[str] = Field(default=None, min_length=1, max_length=500)
        Platform: Optional[str] = Field(default=None, min_length=1, max_length=50)
        Year: Optional[int] = Field(default=None, gt=-1, lt=2030)
        Genre: Optional[str] = Field(default=None, min_length=1, max_length=500)
        Publisher: Optional[str] = Field(default=None, min_length=1, max_length=500)
        North_America: Optional[float] = Field(default=None, ge=-1)
        Europe: Optional[float] = Field(default=None, ge=-1)
        Japan: Optional[float] = Field(default=None, ge=-1)
        Rest_of_World: Optional[float] = Field(default=None, ge=-1)
        Global: Optional[float] = Field(default=None, ge=-1)
        Review: Optional[str] = Field(default=None, max_length=100)

class ConsoleUpdate(SQLModel):
        Console_Name: Optional[str] = Field(default=None, min_length=1, max_length=50)
        Type: Optional[str] = Field(default=None, min_length=1, max_length=50)
        Company: Optional[str] = Field(default=None, min_length=1, max_length=50)
        Released_Year: Optional[int] = Field(default=None, gt=-1, lt=2030)
        Discontinuation_Year: Optional[int] = Field(default=None, gt=-1, lt=2030)
        Units_Sold: Optional[float] = Field(default=None, gt=-1)

###deeleted
class ArchivedGameSQL(SQLModel, table=True):
    # Usamos el mismo 'index' como Primary Key para referencia,
    # pero podría ser un nuevo ID si lo prefieres.
    # Aquí lo mantenemos como PK y referencia al original.
    index: Optional[int] = Field(default=None, primary_key=True) # ID del juego original
    Rank: int
    Game_Title: str
    Platform: str
    Year: int
    Genre: str
    Publisher: str
    North_America: Optional[float] = Field(default=None)
    Europe: Optional[float] = Field(default=None)
    Japan: Optional[float] = Field(default=None)
    Rest_of_World: Optional[float] = Field(default=None)
    Global: Optional[float] = Field(default=None)
    Review: Optional[str] = Field(default=None)
    archived_at: datetime = Field(default_factory=datetime.now) # Marca de tiempo de archivado

class ArchivedConsoleSQL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # ID de la consola original
    Console_Name: str
    Type: str
    Company: str
    Released_Year: int
    Discontinuation_Year: Optional[int] = Field(default=None)
    Units_Sold: Optional[float] = Field(default=None)
    archived_at: datetime = Field(default_factory=datetime.now) # Marca de tiempo de archivado

class Subscriber(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True) # El email será único y se podrá buscar
    subscribed_at: datetime = Field(default_factory=datetime.now)