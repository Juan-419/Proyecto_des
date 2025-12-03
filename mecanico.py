from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Mecanico

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def listar_mecanicos(request: Request, session: Session = Depends(get_session)):
    mecanicos = session.exec(select(Mecanico).where(Mecanico.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "mecanico_list.html",
        {"request": request, "mecanicos": mecanicos}
    )


@router.get("/new", response_class=HTMLResponse)
def formulario_nuevo_mecanico(request: Request):
    return request.app.state.templates.TemplateResponse(
        "mecanico_new.html",
        {"request": request}
    )


@router.post("/new")
def crear_mecanico(
    nombre: str = Form(...),
    especialidad: str = Form(...),
    session: Session = Depends(get_session)
):
    mecanico = Mecanico(nombre=nombre, especialidad=especialidad, active=True)
    session.add(mecanico)
    session.commit()

    return RedirectResponse("/mecanicos", status_code=HTTP_303_SEE_OTHER)


@router.get("/editar/{mecanico_id}", response_class=HTMLResponse)
def editar_mecanico_form(mecanico_id: int, request: Request, session: Session = Depends(get_session)):
    mecanico = session.get(Mecanico, mecanico_id)
    if not mecanico:
        return HTMLResponse("Mecánico no encontrado", status_code=404)

    return request.app.state.templates.TemplateResponse(
        "mecanico_edit.html",
        {"request": request, "mecanico": mecanico}
    )


@router.post("/editar/{mecanico_id}")
def editar_mecanico(
    mecanico_id: int,
    nombre: str = Form(...),
    especialidad: str = Form(...),
    session: Session = Depends(get_session)
):
    mecanico = session.get(Mecanico, mecanico_id)
    if not mecanico:
        return HTMLResponse("Mecánico no encontrado", status_code=404)

    mecanico.nombre = nombre
    mecanico.especialidad = especialidad

    session.add(mecanico)
    session.commit()

    return RedirectResponse("/mecanicos", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminar/{mecanico_id}")
def eliminar_mecanico(mecanico_id: int, session: Session = Depends(get_session)):
    mecanico = session.get(Mecanico, mecanico_id)
    if mecanico:
        mecanico.active = False
        session.add(mecanico)
        session.commit()

    return RedirectResponse("/mecanicos", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminados", response_class=HTMLResponse)
def mecanicos_eliminados(request: Request, session: Session = Depends(get_session)):
    mecanicos = session.exec(select(Mecanico).where(Mecanico.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "mecanico_eliminados.html",
        {"request": request, "mecanicos": mecanicos}
    )


@router.get("/restaurar/{mecanico_id}")
def restaurar_mecanico(mecanico_id: int, session: Session = Depends(get_session)):
    mecanico = session.get(Mecanico, mecanico_id)
    if mecanico:
        mecanico.active = True
        session.add(mecanico)
        session.commit()

    return RedirectResponse("/mecanicos/eliminados", status_code=HTTP_303_SEE_OTHER)
