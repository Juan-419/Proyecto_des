from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from typing import List, Optional
from datetime import datetime

from db import get_session
from models import Cliente
from supa.supabase_upload import upload_to_bucket

router = APIRouter(tags=["Clientes"])
templates = Jinja2Templates(directory="templates")


@router.get("/json", response_model=List[Cliente])
def listar_clientes_json(session: Session = Depends(get_session)):
    return session.exec(select(Cliente).where(Cliente.active == True)).all()


@router.get("/eliminados", response_model=List[Cliente])
def listar_clientes_eliminados(session: Session = Depends(get_session)):
    return session.exec(select(Cliente).where(Cliente.active == False)).all()


@router.get("/", response_class=HTMLResponse)
def listado_clientes_html(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    return templates.TemplateResponse(
        "cliente_list.html",
        {"request": request, "clientes": clientes}
    )


@router.get("/new", response_class=HTMLResponse)
def new_cliente_form(request: Request):
    return templates.TemplateResponse(
        "new_cliente.html",
        {"request": request, "current_year": datetime.now().year}
    )

@router.get("/{cliente_id}", response_class=HTMLResponse)
def get_cliente_detail_html(request: Request, cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.exec(select(Cliente).where(Cliente.id == cliente_id)).first()

    if not cliente:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_msg": f"Cliente con ID {cliente_id} no encontrado."},
            status_code=404,
        )

    return templates.TemplateResponse(
        "cliente_detail.html",
        {"request": request, "user": cliente}
    )



@router.post("/", response_class=RedirectResponse)
async def create_cliente_from_form(
    session: Session = Depends(get_session),
    nombre: str = Form(...),
    anio: int = Form(...),
    status: str = Form(...),
    telefono: Optional[str] = Form(None),
    correo: Optional[str] = Form(None),
    img: Optional[UploadFile] = File(None)
):
    imagen_url = None

    if img and img.filename:
        try:
            imagen_url = await upload_to_bucket(img)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")

    cliente = Cliente(
        nombre=nombre,
        anio=anio,
        active=(status.lower() == "true"),
        telefono=telefono,
        correo=correo,
        img=imagen_url
    )

    session.add(cliente)
    session.commit()
    session.refresh(cliente)

    return RedirectResponse(url="/clientes/", status_code=HTTP_303_SEE_OTHER)
