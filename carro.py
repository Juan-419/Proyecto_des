from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Carro, Cliente

router = APIRouter(tags=["Carros"])


@router.get("/", response_class=HTMLResponse)
def listar_carros(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "carro_list.html",
        {"request": request, "carros": carros}
    )


@router.get("/new", response_class=HTMLResponse)
def formulario_carro(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "new_carro.html",
        {"request": request, "clientes": clientes}
    )


@router.post("/new")
def crear_carro(
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...),
    session: Session = Depends(get_session)
):
    carro = Carro(marca=marca, modelo=modelo, placa=placa, cliente_id=cliente_id)
    session.add(carro)
    session.commit()
    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


@router.get("/editar/{carro_id}", response_class=HTMLResponse)
def editar_carro_form(carro_id: int, request: Request, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if not carro:
        return HTMLResponse("Carro no encontrado", status_code=404)

    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()

    return request.app.state.templates.TemplateResponse(
        "carro_edit.html",
        {"request": request, "carro": carro, "clientes": clientes}
    )


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

    session.add(carro)
    session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminar/{carro_id}")
def eliminar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if carro:
        carro.active = False
        session.add(carro)
        session.commit()
    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminados", response_class=HTMLResponse)
def eliminados(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "carros_eliminados.html",
        {"request": request, "carros": carros}
    )
