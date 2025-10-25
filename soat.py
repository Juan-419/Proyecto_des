from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from db import get_session
from models import SOAT, SOATCreate, Carro, SOATBase 
from sqlmodel import Session


router = APIRouter(prefix="/soats", tags=["SOATs"])



@router.get("/", response_model=List[SOAT], summary="Listar todos los SOATs")
def listar_soats(session: Session = Depends(get_session)):
    return session.exec(select(SOAT)).all()



@router.get("/carro/{carro_id}", response_model=SOAT, summary="Obtener SOAT por ID del carro")
def obtener_soat_por_carro(carro_id: int, session: Session = Depends(get_session)):
    soat = session.exec(select(SOAT).where(SOAT.carro_id == carro_id)).first()
    if not soat:
        raise HTTPException(status_code=404, detail=f"No se encontró SOAT para el carro ID {carro_id}")
    return soat



@router.post("/", response_model=SOAT, status_code=201, summary="Crear un nuevo SOAT")
def crear_soat(nuevo: SOATCreate, session: Session = Depends(get_session)):

    carro = session.get(Carro, nuevo.carro_id)
    if not carro or not carro.active:
        raise HTTPException(status_code=404, detail="Carro no encontrado o inactivo")
        
    existing = session.exec(select(SOAT).where(SOAT.carro_id == nuevo.carro_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El carro ya tiene un SOAT asociado")
        
    soat = SOAT.from_orm(nuevo)
    session.add(soat)
    session.commit()
    session.refresh(soat)
    return soat



@router.get("/{soat_id}", response_model=SOAT, summary="Obtener SOAT por ID")
def obtener_soat(soat_id: int, session: Session = Depends(get_session)):
    soat = session.get(SOAT, soat_id)
    if not soat:
        raise HTTPException(status_code=404, detail="SOAT no encontrado")
    return soat


@router.put("/{soat_id}", response_model=SOAT, summary="Actualizar un registro de SOAT")
def actualizar_soat(soat_id: int, soat_actualizado: SOATBase, session: Session = Depends(get_session)):
    soat_db = session.get(SOAT, soat_id)
    if not soat_db:
        raise HTTPException(status_code=404, detail="SOAT no encontrado")


    if hasattr(soat_actualizado, 'carro_id') and soat_actualizado.carro_id != soat_db.carro_id:
       
        raise HTTPException(status_code=400, detail="El carro_id no puede ser modificado directamente en este endpoint de PUT. Cree un nuevo SOAT para otro carro.")


    update_data = soat_actualizado.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(soat_db, key, value)

    session.add(soat_db)
    session.commit()
    session.refresh(soat_db)
    return soat_db



@router.delete("/{soat_id}", summary="Eliminar físicamente un SOAT")
def eliminar_soat(soat_id: int, session: Session = Depends(get_session)):
    soat = session.get(SOAT, soat_id)
    if not soat:
        raise HTTPException(status_code=404, detail="SOAT no encontrado")

    session.delete(soat)
    session.commit()
    return {"mensaje": f"SOAT {soat_id} eliminado exitosamente"}