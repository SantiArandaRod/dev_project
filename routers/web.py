from typing import Optional
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import csv

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/videojuegos")
def mostrar_videojuegos(request: Request):
    videojuegos = []
    with open("videojuegos.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for fila in reader:
            videojuegos.append(fila)
    return templates.TemplateResponse("videojuegos.html", {"request": request, "videojuegos": videojuegos})
