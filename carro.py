from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from typing import List
from db import get_session
from models import Carro, Cliente

router = APIRouter(prefix="/carros", tags=["Carros"])

templates = Jinja2Templates(directory="templates")



@router.get("/new", response_class=HTMLResponse, summary="Formulario de Nuevo Carro (HTML)")
def new_carro_form(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()

    return templates.TemplateResponse(
        "new_carro.html",
        {"request": request, "clientes": clientes}
    )


@router.post("/new", response_class=RedirectResponse, summary="Crear Carro desde Formulario (HTML)")
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
    session.refresh(nuevo_carro)

    return RedirectResponse(url="/carros/", status_code=HTTP_303_SEE_OTHER)


@router.post("/", response_model=Carro)
def crear_carro(carro: Carro, session: Session = Depends(get_session)):
    session.add(carro)
    session.commit()
    session.refresh(carro)
    return carro


@router.get("/", response_model=List[Carro])
def listar_carros(session: Session = Depends(get_session)):
    return session.exec(select(Carro).where(Carro.active == True)).all()


@router.get("/{carro_id}", response_model=Carro)
def obtener_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado")
    return carro


@router.get("/placa/{carro_placa}", response_model=Carro)
def obtener_carro_por_placa(carro_placa: str, session: Session = Depends(get_session)):
    carro = session.exec(select(Carro).where(Carro.placa == carro_placa)).first()
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado con esa placa")
    return carro


@router.get("/marca/{carro_marca}", response_model=List[Carro])
def obtener_carros_por_marca(carro_marca: str, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.marca == carro_marca)).all()
    if not carros:
        raise HTTPException(status_code=404, detail="No se encontraron carros con esa marca")
    return carros


@router.get("/cliente_id/{carro_cliente_id}", response_model=List[Carro])
def obtener_carros_por_cliente(carro_cliente_id: int, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.cliente_id == carro_cliente_id)).all()
    if not carros:
        raise HTTPException(status_code=404, detail="No se encontraron carros para ese cliente")
    return carros


@router.put("/{carro_id}", response_model=Carro)
def actualizar_carro(carro_id: int, carro_actualizado: Carro, session: Session = Depends(get_session)):
    carro_db = session.get(Carro, carro_id)
    if not carro_db:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    carro_db.marca = carro_actualizado.marca
    carro_db.modelo = carro_actualizado.modelo
    carro_db.placa = carro_actualizado.placa
    carro_db.cliente_id = carro_actualizado.cliente_id

    session.commit()
    session.refresh(carro_db)
    return carro_db


@router.delete("/{carro_id}")
def eliminar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    carro.active = False
    session.commit()
    return {"mensaje": f"Carro {carro_id} marcado como eliminado"}


@router.get("/eliminados", response_model=List[Carro])
def listar_carros_eliminados(session: Session = Depends(get_session)):
    return session.exec(select(Carro).where(Carro.active == False)).all()
