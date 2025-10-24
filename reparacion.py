from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import select
from db import get_session
from models import Reparacion, ReparacionCreate, ReparacionMecanicoLink, Mecanico
from sqlmodel import Session

router = APIRouter()

@router.post("/", response_model=Reparacion, status_code=201)
def crear_reparacion(nueva: ReparacionCreate, session: Session = Depends(get_session)):
    # Validar que el carro exista
    if nueva.carro_id:
        from models import Carro
        carro = session.get(Carro, nueva.carro_id)
        if not carro or not carro.active:
            raise HTTPException(status_code=404, detail="Carro no encontrado para la reparación")
    reparacion = Reparacion(descripcion=nueva.descripcion, fecha=nueva.fecha, costo=nueva.costo, carro_id=nueva.carro_id)
    session.add(reparacion)
    session.commit()
    # Asociar mecánicos si vienen ids
    if nueva.mecanico_ids:
        for mid in nueva.mecanico_ids:
            mecanico = session.get(Mecanico, mid)
            if not mecanico or not mecanico.active:
                session.rollback()
                raise HTTPException(status_code=404, detail=f"Mecánico {mid} no encontrado o inactivo")
            link = ReparacionMecanicoLink(reparacion_id=reparacion.id, mecanico_id=mecanico.id)
            session.add(link)
        session.commit()
    session.refresh(reparacion)
    return reparacion

@router.get("/", response_model=List[Reparacion])
def listar_reparaciones(session: Session = Depends(get_session)):
    return session.exec(select(Reparacion).where(Reparacion.active == True)).all()

@router.get("/{reparacion_id}", response_model=Reparacion)
def obtener_reparacion(reparacion_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    if not reparacion or not reparacion.active:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    return reparacion

@router.get("/buscar/por-descripcion/{texto}", response_model=List[Reparacion])
def buscar_reparaciones_por_descripcion(texto: str, session: Session = Depends(get_session)):
    return session.exec(select(Reparacion).where(Reparacion.descripcion.ilike(f"%{texto}%"), Reparacion.active == True)).all()

@router.delete("/{reparacion_id}")
def eliminar_reparacion(reparacion_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    if not reparacion:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    reparacion.active = False
    session.add(reparacion)
    session.commit()
    return {"mensaje": f"Reparación {reparacion_id} marcada como eliminada"}

@router.get("/eliminadas", response_model=List[Reparacion])
def listar_reparaciones_eliminadas(session: Session = Depends(get_session)):
    return session.exec(select(Reparacion).where(Reparacion.active == False)).all()
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Reparacion

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



@router.post("/", response_model=Reparacion)
def crear_reparacion(reparacion: Reparacion, session: Session = Depends(get_session)):
    session.add(reparacion)
    session.commit()
    session.refresh(reparacion)
    return reparacion


@router.put("/{reparacion_id}", response_model=Reparacion, summary="Actualizar reparación completa")
def actualizar_reparacion(reparacion_id: int, reparacion_actualizada: Reparacion, session: Session = Depends(get_session)):
    reparacion_db = session.get(Reparacion, reparacion_id)
    if not reparacion_db:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")

    reparacion_db.descripcion = reparacion_actualizada.descripcion
    reparacion_db.costo = reparacion_actualizada.costo
    reparacion_db.fecha = reparacion_actualizada.fecha
    reparacion_db.carro_id = reparacion_actualizada.carro_id
    reparacion_db.mecanico_id = reparacion_actualizada.mecanico_id

    session.add(reparacion_db)
    session.commit()
    session.refresh(reparacion_db)
    return reparacion_db


# Borrado lógico
@router.delete("/{reparacion_id}")
def eliminar_reparacion(reparacion_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    if not reparacion:
        raise HTTPException(status_code=404, detail="Reparación no encontrada")
    reparacion.active = False
    session.add(reparacion)
    session.commit()
    return {"mensaje": f"Reparación {reparacion_id} marcada como eliminada"}
