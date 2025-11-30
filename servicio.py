from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, SQLModel, Field, Relationship
from starlette.status import HTTP_303_SEE_OTHER
from typing import List, Optional
from datetime import datetime
from db import get_session

class Carro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patente: str
    cliente_id: Optional[int] = Field(default=None, foreign_key="cliente.id")
    servicios: List["Servicio"] = Relationship(back_populates="carro") 


class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_inicio: datetime = Field(default_factory=datetime.now)
    descripcion: str
    costo: float
    estado: str = Field(default="Pendiente", description="Ej: Pendiente, En Progreso, Finalizado")
    

    carro_id: Optional[int] = Field(default=None, foreign_key="carro.id")
    carro: Carro = Relationship(back_populates="servicios")


router = APIRouter(prefix="/servicios", tags=["Servicios"])
templates = Jinja2Templates(directory="templates")


@router.get("/new", response_class=HTMLResponse, summary="Formulario de Nuevo Servicio (HTML)")
def new_servicio_form(request: Request, carro_id: Optional[int] = None, session: Session = Depends(get_session)):
    """
    Muestra el formulario para registrar un nuevo servicio. 
    Recibe opcionalmente el ID del carro.
    """
    carro = None
    if carro_id:
        carro = session.get(Carro, carro_id)
        if not carro:
            return templates.TemplateResponse(
                "error.html", 
                {"request": request, "error_msg": f"Carro con ID {carro_id} no encontrado."},
                status_code=status.HTTP_404_NOT_FOUND
            )

    return templates.TemplateResponse(
        "new_servicio.html",
        {"request": request, "carro": carro}
    )


@router.get("/carro/{carro_id}", response_class=HTMLResponse, summary="Lista de Servicios de un Carro (HTML)")
def list_servicios_by_carro_html(request: Request, carro_id: int, session: Session = Depends(get_session)):
    """Muestra la lista de servicios de un vehículo en la interfaz HTML."""
    
    carro = session.get(Carro, carro_id)
    if not carro:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error_msg": f"Carro con ID {carro_id} no encontrado."},
            status_code=status.HTTP_404_NOT_FOUND
        )
    servicios = session.exec(
        select(Servicio).where(Servicio.carro_id == carro_id).order_by(Servicio.fecha_inicio.desc())
    ).all()
    
    return templates.TemplateResponse(
        "carro_servicios.html", # Nuevo template para mostrar la lista
        {"request": request, "carro": carro, "servicios": servicios} 
    )


@router.post("/", response_class=RedirectResponse, summary="Crear Servicio desde Formulario (HTML)")
def create_servicio_from_form(
    session: Session = Depends(get_session),
    carro_id: int = Form(...),
    descripcion: str = Form(...),
    costo: float = Form(...),
    estado: str = Form(...) 
    """Procesa el formulario y guarda el nuevo servicio en la DB."""
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail=f"Carro con ID {carro_id} no existe.")

    servicio_data = Servicio(
        carro_id=carro_id,
        descripcion=descripcion,
        costo=costo,
        estado=estado,
    )

    session.add(servicio_data)
    session.commit()
    session.refresh(servicio_data)

    return RedirectResponse(
        url=f"/servicios/carro/{carro_id}",
        status_code=HTTP_303_SEE_OTHER
    )