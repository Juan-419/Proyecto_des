from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from db import get_session
from models import SOAT, SOATCreate, Carro
from sqlmodel import Session

router = APIRouter()

@router.post("/", response_model=SOAT, status_code=201)
def crear_soat(nuevo: SOATCreate, session: Session = Depends(get_session)):
    carro = session.get(Carro, nuevo.carro_id)
    if not carro or not carro.active:
        raise HTTPException(status_code=404, detail="Carro no encontrado")
    existing = session.exec(select(SOAT).where(SOAT.carro_id == nuevo.carro_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="El carro ya tiene un SOAT")
    soat = SOAT(**nuevo.dict())
    session.add(soat)
    session.commit()
    session.refresh(soat)
    return soat

@router.get("/{soat_id}", response_model=SOAT)
def obtener_soat(soat_id: int, session: Session = Depends(get_session)):
    soat = session.get(SOAT, soat_id)
    if not soat:
        raise HTTPException(status_code=404, detail="SOAT no encontrado")
    return soat
