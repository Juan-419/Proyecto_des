from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Carro

router = APIRouter(prefix="/carros", tags=["Carros"])

# 🟢 Crear un carro
@router.post("/", response_model=Carro, summary="Crear un nuevo carro")
def crear_carro(carro: Carro, session: Session = Depends(get_session)):
    session.add(carro)
    session.commit()
    session.refresh(carro)
    return carro

# 🔵 Listar todos los carros activos
@router.get("/", response_model=List[Carro], summary="Listar todos los carros activos")
def listar_carros(session: Session = Depends(get_session)):
    return session.exec(select(Carro).where(Carro.active == True)).all()

# 🔍 Obtener carro por ID
@router.get("/{carro_id}", response_model=Carro, summary="Obtener carro por ID")
def obtener_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado")
    return carro

# 🔎 Obtener carro por placa
@router.get("/placa/{carro_placa}", response_model=Carro, summary="Buscar carro por placa")
def obtener_carro_por_placa(carro_placa: str, session: Session = Depends(get_session)):
    carro = session.exec(select(Carro).where(Carro.placa == carro_placa)).first()
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado con esa placa")
    return carro

# 🔎 Buscar carros por marca
@router.get("/marca/{carro_marca}", response_model=List[Carro], summary="Buscar carros por marca")
def obtener_carros_por_marca(carro_marca: str, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.marca == carro_marca)).all()
    if not carros:
        raise HTTPException(status_code=404, detail="No se encontraron carros con esa marca")
    return carros

# 🔎 Buscar carros por cliente_id (puede devolver varios)
@router.get("/cliente_id/{carro_cliente_id}", response_model=List[Carro], summary="Buscar carros por ID del cliente")
def obtener_carros_por_cliente(carro_cliente_id: int, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.cliente_id == carro_cliente_id)).all()
    if not carros:
        raise HTTPException(status_code=404, detail="No se encontraron carros para ese cliente")
    return carros

# 🔄 Actualizar carro completo (PUT)
@router.put("/{carro_id}", response_model=Carro, summary="Actualizar un carro completo")
def actualizar_carro(carro_id: int, carro_actualizado: Carro, session: Session = Depends(get_session)):
    carro_db = session.get(Carro, carro_id)
    if not carro_db:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    carro_db.marca = carro_actualizado.marca
    carro_db.modelo = carro_actualizado.modelo
    carro_db.placa = carro_actualizado.placa
    carro_db.cliente_id = carro_actualizado.cliente_id

    session.add(carro_db)
    session.commit()
    session.refresh(carro_db)
    return carro_db

# 🔴 Borrado lógico (no elimina el registro)
@router.delete("/{carro_id}", summary="Eliminar un carro (borrado lógico)")
def eliminar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    carro.active = False
    session.add(carro)
    session.commit()
    return {"mensaje": f"Carro {carro_id} marcado como eliminado"}

# ⚪ Listar carros eliminados
@router.get("/eliminados", response_model=List[Carro], summary="Listar carros eliminados")
def listar_carros_eliminados(session: Session = Depends(get_session)):
    return session.exec(select(Carro).where(Carro.active == False)).all()
