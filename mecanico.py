from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Mecanico

router = APIRouter(prefix="/mecanicos", tags=["Mecanicos"])

@router.get("/", response_model=List[Mecanico])
def listar_mecanicos(session: Session = Depends(get_session)):
    return session.exec(select(Mecanico).where(Mecanico.active == True)).all()

@router.get("/eliminados", response_model=List[Mecanico])
def listar_mecanicos_eliminados(session: Session = Depends(get_session)):
    return session.exec(select(Mecanico).where(Mecanico.active == False)).all()

@router.get("/{mecanico_id}", response_model=Mecanico)
def obtener_mecanico(mecanico_id: int, session: Session = Depends(get_session)):
    mecanico = session.get(Mecanico, mecanico_id)
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")
    return mecanico

@router.post("/", response_model=Mecanico)
def crear_mecanico(mecanico: Mecanico, session: Session = Depends(get_session)):
    session.add(mecanico)
    session.commit()
    session.refresh(mecanico)
    return mecanico

@router.delete("/{mecanico_id}")
def eliminar_mecanico(mecanico_id: int, session: Session = Depends(get_session)):
    mecanico = session.get(Mecanico, mecanico_id)
    if not mecanico:
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")
    mecanico.active = False
    session.add(mecanico)
    session.commit()
    return {"mensaje": f"Mecánico {mecanico_id} marcado como eliminado"}

@router.put("/{mecanico_id}", response_model=Mecanico)
def actualizar_mecanico(mecanico_id: int, mecanico_actualizado: Mecanico, session: Session = Depends(get_session)):
    mecanico_db = session.get(Mecanico, mecanico_id)
    if not mecanico_db:
        raise HTTPException(status_code=404, detail="Mecánico no encontrado")

    mecanico_db.nombre = mecanico_actualizado.nombre
    mecanico_db.especialidad = mecanico_actualizado.especialidad

    session.add(mecanico_db)
    session.commit()
    session.refresh(mecanico_db)
    return mecanico_db
