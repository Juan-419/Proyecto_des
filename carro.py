from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Carro, Cliente

router = APIRouter()


# ---------- FORMULARIO PARA REGISTRAR ----------
@router.get("/new", response_class=HTMLResponse)
def nuevo_carro_form(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "new_carro.html",
        {"request": request, "clientes": clientes}
    )


# ---------- CREAR (HTML FORM) ----------
@router.post("/new")
def crear_carro(
    request: Request,
    session: Session = Depends(get_session),
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...)
):
    carro = Carro(
        marca=marca,
        modelo=modelo,
        placa=placa,
        cliente_id=cliente_id,
        active=True
    )
    session.add(carro)
    session.commit()
    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


# ---------- LISTADO HTML ----------
@router.get("/", response_class=HTMLResponse)
def listar_carros(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "carro_list.html", 
        {"request": request, "carros": carros}
    )


# ---------- EDITAR FORM ----------
@router.get("/editar/{carro_id}", response_class=HTMLResponse)
def editar_carro_form(carro_id: int, request: Request, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()

    if not carro:
        return HTMLResponse("Carro no encontrado", status_code=404)

    return request.app.state.templates.TemplateResponse(
        "carro_edit.html",
        {"request": request, "carro": carro, "clientes": clientes}
    )


# ---------- EDITAR POST ----------
@router.post("/editar/{carro_id}")
def editar_carro(
    carro_id: int,
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...),
    session: Session = Depends(get_session)
):
    carro = session.get(Carro, carro_id)

    if not carro:
        return HTMLResponse("Carro no encontrado", status_code=404)

    carro.marca = marca
    carro.modelo = modelo
    carro.placa = placa
    carro.cliente_id = cliente_id

    session.commit()
    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


# ---------- ELIMINAR (SOFT DELETE) ----------
@router.get("/eliminar/{carro_id}")
def eliminar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)

    if carro:
        carro.active = False
        session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


# ---------- LISTAR ELIMINADOS ----------
@router.get("/eliminados", response_class=HTMLResponse)
def eliminados(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "carro_eliminados.html",
        {"request": request, "carros": carros}
    )


# ---------- RESTAURAR ----------
@router.get("/restaurar/{carro_id}")
def restaurar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)

    if carro:
        carro.active = True
        session.commit()

    return RedirectResponse("/carros/eliminados", status_code=HTTP_303_SEE_OTHER)
