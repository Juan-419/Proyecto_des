from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from db import get_session
from models import Cliente

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[Cliente])
def listar_clientes(session: Session = Depends(get_session)):
    return session.exec(select(Cliente).where(Cliente.active == True)).all()


@router.get("/eliminados", response_model=List[Cliente])
def listar_clientes_eliminados(session: Session = Depends(get_session)):
    return session.exec(select(Cliente).where(Cliente.active == False)).all()



@router.get("/correo/{cliente_correo}", response_model=Cliente)
def obtener_cliente_por_correo(cliente_correo: str, session: Session = Depends(get_session)):
    cliente = session.exec(select(Cliente).where(Cliente.correo == cliente_correo)).first()
    if not cliente:
      raise HTTPException(status_code=404, detail="Cliente no encontrado o correo mal digitado")
    return cliente


@router.get("/{cliente_id}", response_model=Cliente)
def obtener_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/telefono/{cliente_telefono}", response_model=Cliente)
def obtener_cliente_por_telefono(cliente_telefono: int, session: Session = Depends(get_session)):
    cliente = session.exec(select(Cliente).where(Cliente.telefono == cliente_telefono)).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=Cliente)
def crear_cliente(cliente: Cliente, session: Session = Depends(get_session)):
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente



@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.active = False
    session.add(cliente)
    session.commit()
    return {"mensaje": f"Cliente {cliente_id} marcado como eliminado"}

    
    

@router.put("/{cliente_id}", response_model=Cliente, summary="Actualizar cliente completo")
def actualizar_cliente(cliente_id: int, cliente_actualizado: Cliente, session: Session = Depends(get_session)):
    cliente_db = session.get(Cliente, cliente_id)
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente_db.nombre = cliente_actualizado.nombre
    cliente_db.telefono = cliente_actualizado.telefono
    cliente_db.correo = cliente_actualizado.correo

    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    return cliente_db