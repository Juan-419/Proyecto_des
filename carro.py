from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Carro, Cliente
from supa.supabase_upload import upload_to_bucket

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def listar_carros(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    
    return request.app.state.templates.TemplateResponse(
        "carro_list.html",
        {"request": request, "carros": carros}
    )


@router.get("/new", response_class=HTMLResponse)
def formulario_nuevo_carro(request: Request, session: Session = Depends(get_session)):
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()
    
    return request.app.state.templates.TemplateResponse(
        "new_carro.html",
        {"request": request, "clientes": clientes}
    )


@router.post("/new")
async def crear_carro(
    request: Request,
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...),
    img: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    nuevo_carro = Carro(
        marca=marca,
        modelo=modelo,
        placa=placa,
        cliente_id=cliente_id,
    )

    if img:
        url = await upload_to_bucket(img, "carros")
        nuevo_carro.img = url

    session.add(nuevo_carro)
    session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)


@router.get("/editar/{carro_id}", response_class=HTMLResponse)
def editar_carro_form(carro_id: int, request: Request, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    clientes = session.exec(select(Cliente).where(Cliente.active == True)).all()

    return request.app.state.templates.TemplateResponse(
        "carro_edit.html",
        {"request": request, "carro": carro, "clientes": clientes}
    )



@router.post("/editar/{carro_id}")
async def editar_carro(
    carro_id: int,
    marca: str = Form(...),
    modelo: str = Form(...),
    placa: str = Form(...),
    cliente_id: int = Form(...),
    img: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    carro = session.get(Carro, carro_id)

    carro.marca = marca
    carro.modelo = modelo
    carro.placa = placa
    carro.cliente_id = cliente_id

    if img:
        url = await upload_to_bucket(img, "carros")
        carro.img = url

    session.add(carro)
    session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)



@router.get("/eliminar/{carro_id}")
def eliminar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    carro.active = False
    session.add(carro)
    session.commit()

    return RedirectResponse("/carros", status_code=HTTP_303_SEE_OTHER)



@router.get("/eliminados", response_class=HTMLResponse)
def eliminados(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "carros_eliminados.html",
        {"request": request, "carros": carros}
    )



@router.get("/restaurar/{carro_id}")
def restaurar_carro(carro_id: int, session: Session = Depends(get_session)):
    carro = session.get(Carro, carro_id)
    carro.active = True
    session.add(carro)
    session.commit()

    return RedirectResponse("/carros/eliminados", status_code=HTTP_303_SEE_OTHER)
