from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, SQLModel, Field, Relationship
from starlette.status import HTTP_303_SEE_OTHER
from typing import List, Optional
from db import get_session 
from supabase import upload_to_bucket 

class Carro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: Optional[int] = Field(default=None, foreign_key="cliente.id")
    cliente: "Cliente" = Relationship(back_populates="carros") 

class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str 
    telefono: Optional[str] = None 
    correo: Optional[str] = None 
    active: bool = True 
    anio: Optional[int] = None
    status: bool = True 
    img: Optional[str] = None

    carros: List[Carro] = Relationship(back_populates="cliente") 

router = APIRouter(tags=["Clientes"])


templates = Jinja2Templates(directory="templates")


@router.get("/", response_model=List[Cliente], include_in_schema=False)
def listar_clientes_json(session: Session = Depends(get_session)):
    """Ruta original para API que lista clientes activos (JSON)"""
    return session.exec(select(Cliente).where(Cliente.active == True)).all()


@router.get("/eliminados", response_model=List[Cliente], include_in_schema=False)
def listar_clientes_eliminados(session: Session = Depends(get_session)):
    """Ruta original para API que lista clientes eliminados (JSON)"""
    return session.exec(select(Cliente).where(Cliente.active == False)).all()


@router.get("/", response_class=HTMLResponse, summary="Listado de Clientes (HTML)")
def listado_clientes_html(request: Request, session: Session = Depends(get_session)):
    """Muestra la lista de clientes en la interfaz HTML."""
    # Consulta la lista de clientes activos
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    
    return templates.TemplateResponse(
        "cliente_list.html", # Tu template renombrado
        {"request": request, "clientes": clientes} 
    )

@router.get("/new", response_class=HTMLResponse, summary="Formulario de Nuevo Cliente (HTML)")
def new_cliente_form(request: Request):
    """Muestra el formulario para registrar un nuevo cliente (new_cliente.html)."""
    return templates.TemplateResponse(
        "new_cliente.html",
        {"request": request}
    )

@router.get("/{cliente_id}", response_class=HTMLResponse, summary="Detalle de Cliente (HTML)")
def get_cliente_detail_html(request: Request, cliente_id: int, session: Session = Depends(get_session)):
    """Muestra el detalle de un cliente con sus carros en HTML."""

    cliente = session.exec(
        select(Cliente).where(Cliente.id == cliente_id)
    ).first()
    
    if not cliente:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error_msg": f"Cliente con ID {cliente_id} no encontrado."},
            status_code=404
        )

    return templates.TemplateResponse(
        "cliente_detail.html",
        {"request": request, "user": cliente}
    )

@router.post("/", response_class=RedirectResponse, summary="Crear Cliente desde Formulario (HTML)")
async def create_cliente_from_form(
    session: Session = Depends(get_session),
    nombre: str = Form(...),
    anio: int = Form(...),
    status: str = Form(..., alias="status"), 
    telefono: Optional[str] = Form(None),
    correo: Optional[str] = Form(None),
    img: Optional[UploadFile] = File(None)
):
    """Procesa el formulario, sube la imagen a Supabase y guarda el cliente en la DB."""
    imagen_url = None

    if img and img.filename:
        try:
            imagen_url = await upload_to_bucket(img)
        except Exception as e:
            print(f"Error CRÍTICO al subir imagen a Supabase: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error al subir imagen: {str(e)}"
            )
    cliente_data = Cliente(
        nombre=nombre,
        anio=anio,
        active=(status.lower() == 'true'), 
        telefono=telefono,
        correo=correo,
        img=imagen_url
    )
    session.add(cliente_data)
    session.commit()
    session.refresh(cliente_data)

    return RedirectResponse(url="/clientes/", status_code=HTTP_303_SEE_OTHER)