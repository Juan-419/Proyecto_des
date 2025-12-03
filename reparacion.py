from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import get_session
from models import Reparacion, ReparacionCreate, Carro, Mecanico, ReparacionMecanicoLink

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])


@router.get("/", response_class=HTMLResponse)
def listado_reparaciones(request: Request, session: Session = Depends(get_session)):
    reparaciones = session.exec(select(Reparacion).where(Reparacion.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "reparacion_list.html",
        {"request": request, "reparaciones": reparaciones}
    )


@router.get("/new", response_class=HTMLResponse)
def form_nueva_reparacion(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    mecanicos = session.exec(select(Mecanico).where(Mecanico.active == True)).all()
    return request.app.state.templates.TemplateResponse(
        "new_reparacion.html",
        {"request": request, "carros": carros, "mecanicos": mecanicos}
    )


@router.post("/new")
def crear_reparacion(
    descripcion: str = Form(...),
    fecha: str = Form(...),
    costo: float = Form(...),
    carro_id: int = Form(...),
    mecanico_ids: list[int] = Form([]),
    session: Session = Depends(get_session)
):
    carro = session.get(Carro, carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro no encontrado")

    reparacion = Reparacion(
        descripcion=descripcion,
        fecha=fecha,
        costo=costo,
        carro_id=carro_id
    )
    session.add(reparacion)
    session.commit()
    session.refresh(reparacion)

    for mid in mecanico_ids:
        session.add(ReparacionMecanicoLink(reparacion_id=reparacion.id, mecanico_id=mid))

    session.commit()
    return RedirectResponse("/reparaciones", status_code=HTTP_303_SEE_OTHER)


@router.get("/editar/{reparacion_id}", response_class=HTMLResponse)
def form_editar_reparacion(reparacion_id: int, request: Request, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    mecanicos = session.exec(select(Mecanico).where(Mecanico.active == True)).all()

    return request.app.state.templates.TemplateResponse(
        "reparacion_edit.html",
        {"request": request, "r": reparacion, "carros": carros, "mecanicos": mecanicos}
    )

@router.post("/editar/{reparacion_id}")
def editar_reparacion(
    reparacion_id: int,
    descripcion: str = Form(...),
    fecha: str = Form(...),
    costo: float = Form(...),
    carro_id: int = Form(...),
    mecanico_ids: list[int] = Form([]),
    session: Session = Depends(get_session)
):
    reparacion = session.get(Reparacion, reparacion_id)

    reparacion.descripcion = descripcion
    reparacion.fecha = fecha
    reparacion.costo = costo
    reparacion.carro_id = carro_id

    session.exec(
        select(ReparacionMecanicoLink)
        .where(ReparacionMecanicoLink.reparacion_id == reparacion_id)
    ).all()

    for mid in mecanico_ids:
        session.add(ReparacionMecanicoLink(reparacion_id=reparacion_id, mecanico_id=mid))

    session.commit()
    return RedirectResponse("/reparaciones", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminar/{reparacion_id}")
def eliminar_reparacion(reparacion_id: int, session: Session = Depends(get_session)):
    reparacion = session.get(Reparacion, reparacion_id)
    reparacion.active = False
    session.commit()
    return RedirectResponse("/reparaciones", status_code=HTTP_303_SEE_OTHER)


@router.get("/eliminadas", response_class=HTMLResponse)
def reparaciones_eliminadas(request: Request, session: Session = Depends(get_session)):
    reps = session.exec(select(Reparacion).where(Reparacion.active == False)).all()
    return request.app.state.templates.TemplateResponse(
        "reparacion_eliminadas.html",
        {"request": request, "reparaciones": reps}
    )
