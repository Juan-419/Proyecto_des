from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from models import Carro, Mecanico, Reparacion, ReparacionMecanicoLink
from sqlmodel import Session, select
from db import get_session

router = APIRouter()



@router.get("/", response_class=HTMLResponse)
def reparaciones_html(request: Request, session: Session = Depends(get_session)):
    reparaciones = session.exec(
        select(Reparacion).where(Reparacion.active == True)
    ).all()

    carros = {c.id: c for c in session.exec(select(Carro)).all()}
    mecanicos_por_rep = {}

    for rep in reparaciones:
        links = session.exec(
            select(ReparacionMecanicoLink).where(
                ReparacionMecanicoLink.reparacion_id == rep.id
            )
        ).all()

        mecanicos = []
        for l in links:
            mec = session.get(Mecanico, l.mecanico_id)
            if mec:
                mecanicos.append(mec)

        mecanicos_por_rep[rep.id] = mecanicos

    return request.app.state.templates.TemplateResponse(
        "reparacion_list.html",
        {
            "request": request,
            "reparaciones": reparaciones,
            "carros": carros,
            "mecanicos_por_rep": mecanicos_por_rep
        }
    )



@router.get("/new", response_class=HTMLResponse)
def nueva_reparacion_html(request: Request, session: Session = Depends(get_session)):
    carros = session.exec(select(Carro).where(Carro.active == True)).all()
    mecanicos = session.exec(select(Mecanico).where(Mecanico.active == True)).all()

    return request.app.state.templates.TemplateResponse(
        "reparacion_new.html",
        {"request": request, "carros": carros, "mecanicos": mecanicos}
    )



@router.post("/new")
def crear_reparacion_html(
    request: Request,
    carro_id: int = Form(...),
    descripcion: str = Form(...),
    costo: float = Form(...),
    fecha: str = Form(...),
    mecanico_ids: list[int] = Form([]),
    session: Session = Depends(get_session)
):
    reparacion = Reparacion(
        descripcion=descripcion,
        costo=costo,
        fecha=fecha,
        carro_id=carro_id
    )

    session.add(reparacion)
    session.commit()
    session.refresh(reparacion)

    for mid in mecanico_ids:
        session.add(ReparacionMecanicoLink(
            reparacion_id=reparacion.id,
            mecanico_id=mid
        ))

    session.commit()

    return RedirectResponse("/reparaciones", status_code=HTTP_303_SEE_OTHER)
