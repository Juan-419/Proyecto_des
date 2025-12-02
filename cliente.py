from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Cliente
from supa.supabase_upload import upload_to_bucket

router = APIRouter()



@router.get("/", response_class=HTMLResponse)
def listado_clientes_html(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "clientes.html",
        {"request": request, "clientes": clientes}
    )



@router.get("/editar/{cliente_id}", response_class=HTMLResponse)
def editar_cliente_form(cliente_id: int, request: Request, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        return HTMLResponse("Cliente no encontrado", status_code=404)

    return request.app.state.templates.TemplateResponse(
        "cliente_edit.html",
        {"request": request, "cliente": cliente}
    )



@router.post("/editar/{cliente_id}")
async def editar_cliente(
    cliente_id: int,
    nombre: str = Form(...),
    telefono: str = Form(""),
    correo: str = Form(""),
    anio: int = Form(...),
    img: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        return HTMLResponse("Cliente no encontrado", status_code=404)

    cliente.nombre = nombre
    cliente.telefono = telefono
    cliente.correo = correo
    cliente.anio = anio

    
    if img:
        url = await upload_to_bucket(img, "clientes")
        cliente.img = url

    session.add(cliente)
    session.commit()

    return RedirectResponse("/clientes", status_code=HTTP_303_SEE_OTHER)



@router.get("/eliminar/{cliente_id}")
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if cliente:
        cliente.active = False
        session.add(cliente)
        session.commit()

    return RedirectResponse("/clientes", status_code=HTTP_303_SEE_OTHER)



@router.get("/eliminados", response_class=HTMLResponse)
def eliminados(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "cliente_eliminados.html",
        {"request": request, "clientes": clientes}
    )



@router.get("/restaurar/{cliente_id}")
def restaurar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if cliente:
        cliente.active = True
        session.add(cliente)
        session.commit()

    return RedirectResponse("/clientes/eliminados", status_code=HTTP_303_SEE_OTHER)
