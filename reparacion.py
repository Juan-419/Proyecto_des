from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from db import get_session
from models import Reparacion, ReparacionCreate, ReparacionMecanicoLink, Mecanico, Carro

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])


@router.get("/", response_model=List[Reparacion])
def listar_reparaciones(session: Session = Depends(get_session)):
    return session.exec(select(Reparacion).where(Reparacion.active == True)).all()


@router.get("/eliminadas", response_model=List[Reparacion])
def listar_reparaciones_eliminadas(session: Session = Depends(get_session)):
    return session.exec(select(Reparacion).where(Reparacion.active == False)).all()


@router.get("/{reparacion_id}", response_model=Reparacion)
def obtener_reparacion(reparacion_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    if not reparacion:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    return reparacion


@router.post("/", response_model=Reparacion, status_code=201)
def crear_reparacion(nueva: ReparacionCreate, session: Session = Depends(get_session)):

    carro = session.get(Carro, nueva.carro_id)
    if not carro or not carro.active:
        raise HTTPException(status_code=404, detail="Carro no encontrado o inactivo")

    reparacion = Reparacion(
        descripcion=nueva.descripcion,
        fecha=nueva.fecha,
        costo=nueva.costo,
        carro_id=nueva.carro_id
    )

    session.add(reparacion)
    session.commit()
    session.refresh(reparacion)

    # Asociar mecánicos
    for mid in nueva.mecanico_ids or []:
        mecanico = session.get(Mecanico, mid)
        if not mecanico or not mecanico.active:
            raise HTTPException(status_code=404, detail=f"Mecánico {mid} no encontrado o inactivo")

        session.add(ReparacionMecanicoLink(
            reparacion_id=reparacion.id,
            mecanico_id=mecanico.id
        ))

    session.commit()
    session.refresh(reparacion)
    return reparacion


@router.put("/{reparacion_id}", response_model=Reparacion)
def actualizar_reparacion(reparacion_id: int, actualizada: ReparacionCreate, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    if not reparacion:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    reparacion.descripcion = actualizada.descripcion
    reparacion.fecha = actualizada.fecha
    reparacion.costo = actualizada.costo
    reparacion.carro_id = actualizada.carro_id

    session.add(reparacion)
    session.commit()
    session.refresh(reparacion)

    return reparacion


@router.delete("/{reparacion_id}")
def eliminar_reparacion(carro_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, carro_id)
    if not reparacion:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    reparacion.active = False
    session.add(reparacion)
    session.commit()

    return {"message": "Reparación eliminada correctamente"}
