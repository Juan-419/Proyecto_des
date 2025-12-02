from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from typing import List
from db import get_session
from models import Carro, Cliente

router = APIRouter(prefix="/carros", tags=["Carros"])



@router.get("/", response_class=HTMLResponse)
def listar_carros_html(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(
        select(Carro).where(Carro.active == True)
    ).all()

    return request.app.state.templates.TemplateResponse(
        "carros_list.html",
        {"request": request, "carros": carros}
    )



@router.get("/new", response_class=HTMLResponse)
def new_carro_form(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()

    return request.app.state.templates.TemplateResponse(
        "new_carro.html",
        {"request": request, "clientes": clientes}
    )



@router.post("/new")
def create_carro_from_form(
    session: Session = Depends(get_session),
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...)
):
    nuevo_carro = Carro(
        marca=marca,
        modelo=modelo,
        placa=placa,
        cliente_id=cliente_id,
        active=True
    )

    session.add(nuevo_carro)
    session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)
