from fastapi import FastAPI, Request, Depends, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from starlette.status import HTTP_303_SEE_OTHER
from db import create_db_and_tables, get_session
from cliente import router as cliente_router
from carro import router as carro_router
from mecanico import router as mecanico_router
from reparacion import router as reparacion_router
from soat import router as soat_router
from reporte import router as reportes_router
from supa.supabase_upload import upload_to_bucket
from supabase import create_client

app = FastAPI(title="Taller de Carros API")

templates = Jinja2Templates(directory="templates")

# 🔥 IMPORTANTE: MONTAR templates EN EL STATE PARA QUE CLIENTE.PY LO USE
app.state.templates = templates


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("Base de datos inicializada y servidor listo.")


app.include_router(cliente_router, prefix="/clientes", tags=["Clientes"])
app.include_router(carro_router, prefix="/carros", tags=["Carros"])
app.include_router(mecanico_router, prefix="/mecanicos", tags=["Mecánicos"])
app.include_router(reparacion_router, prefix="/reparaciones", tags=["Reparaciones"])
app.include_router(soat_router, prefix="/soats", tags=["SOATs"])
app.include_router(reportes_router)


@app.get("/", response_class=HTMLResponse, tags=["Vistas HTML"])
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "texto": "Bienvenido a la página de tu taller de confianza",
            "titulo_pagina": "Taller de Carros - Inicio"
        }
    )
