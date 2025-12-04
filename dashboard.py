from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from db import get_session
from models import Cliente, Carro, Mecanico, Reparacion

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    total_clientes = session.exec(select(Cliente)).count()
    total_carros = session.exec(select(Carro)).count()
    total_mecanicos = session.exec(select(Mecanico)).count()
    total_reparaciones = session.exec(select(Reparacion)).count()
    reparaciones_activas = session.exec(
        select(Reparacion).where(Reparacion.active == True)
    ).count()

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_clientes": total_clientes,
            "total_carros": total_carros,
            "total_mecanicos": total_mecanicos,
            "total_reparaciones": total_reparaciones,
            "reparaciones_activas": reparaciones_activas
        }
    )
