from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from db import get_session
from models import Cliente, Carro, Mecanico, Reparacion

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    
    total_clientes = len(session.exec(select(Cliente)).all())
    total_carros = len(session.exec(select(Carro)).all())
    total_mecanicos = len(session.exec(select(Mecanico)).all())
    total_reparaciones = len(session.exec(select(Reparacion)).all())
    reparaciones_activas = len(
        session.exec(select(Reparacion).where(Reparacion.active == True)).all()
    )

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
