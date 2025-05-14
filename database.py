from sqlalchemy import Column, Float, ForeignKey, Table, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Games(Base):
    __tablename__ = "games"
    index:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Rank:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Game_Title:Mapped[str] = mapped_column(String(100),nullable=False)
    Platform: Mapped[str] = mapped_column(String(25), nullable=False)
    Year: Mapped[int] = mapped_column(Integer, nullable=False)
    Genre: Mapped[str] = mapped_column(Integer, nullable=False)
    Publisher: Mapped[str] = mapped_column(String(25), nullable=False)
    North_America: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    Europe: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    Japan: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    Rest_of_World: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    Global: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    Review: Mapped[int] = mapped_column(primary_key=True, nullable=False)
