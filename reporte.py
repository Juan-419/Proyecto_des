# reporte.py  (o reports.py)
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from db import get_session
from models import Cliente, Carro, Mecanico, Reparacion, SOAT
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from typing import Optional

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get(
    "/general/pdf",
    response_class=FileResponse,
    responses={200: {"content": {"application/pdf": {"example": "PDF file"}}}},
    summary="Generar reporte general detallado en PDF",
    description="Genera un reporte PDF con listas detalladas de clientes, carros, mecánicos, reparaciones y SOATs."
)
def generar_reporte_pdf(session: Session = Depends(get_session)):
    # Consultas
    clientes = session.exec(select(Cliente)).all()
    carros = session.exec(select(Carro)).all()
    mecanicos = session.exec(select(Mecanico)).all()
    reparaciones = session.exec(select(Reparacion)).all()
    soats = session.exec(select(SOAT)).all()   # <- usar nombre en minúscula

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle("Reporte Detallado del Taller")

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(170, 770, "Reporte Detallado del Taller")

    y = 740
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Total Clientes: {len(clientes)} | Carros: {len(carros)} | Mecánicos: {len(mecanicos)} | Reparaciones: {len(reparaciones)} | SOATs: {len(soats)}")
    y -= 30

    # === Sección de Clientes ===
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Clientes:")
    y -= 20
    c.setFont("Helvetica", 11)
    for cliente in clientes:
        if y < 60:  # salto de página
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        nombre = getattr(cliente, "nombre", "")
        telefono = getattr(cliente, "telefono", "")
        correo = getattr(cliente, "correo", "")
        c.drawString(60, y, f"ID: {cliente.id} | Nombre: {nombre} | Teléfono: {telefono} | Correo: {correo}")
        y -= 15

    # === Sección de Carros ===
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Carros:")
    y -= 20
    c.setFont("Helvetica", 11)
    for carro in carros:
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        marca = getattr(carro, "marca", "")
        modelo = getattr(carro, "modelo", "")
        placa = getattr(carro, "placa", "")
        cliente_id = getattr(carro, "cliente_id", "")
        c.drawString(60, y, f"ID: {carro.id} | Marca: {marca} | Modelo: {modelo} | Placa: {placa} | Cliente ID: {cliente_id}")
        y -= 15

    # === Sección de Mecánicos ===
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Mecánicos:")
    y -= 20
    c.setFont("Helvetica", 11)
    for mec in mecanicos:
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        nombre = getattr(mec, "nombre", "")
        especialidad = getattr(mec, "especialidad", "")
        c.drawString(60, y, f"ID: {mec.id} | Nombre: {nombre} | Especialidad: {especialidad}")
        y -= 15

    # === Sección de Reparaciones ===
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Reparaciones:")
    y -= 20
    c.setFont("Helvetica", 11)
    for rep in reparaciones:
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        descripcion = getattr(rep, "descripcion", "")
        costo = getattr(rep, "costo", "")
        fecha = getattr(rep, "fecha", "")
        c.drawString(60, y, f"ID: {rep.id} | Descripción: {descripcion} | Costo: {costo} | Fecha: {fecha}")
        y -= 15

    # === Sección de SOAT ===
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "SOATs:")
    y -= 20
    c.setFont("Helvetica", 11)
    for s in soats:
        if y < 60:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        carro_id = getattr(s, "carro_id", "")
        numero = getattr(s, "numero", "")
        fecha_vig = getattr(s, "fecha_vigencia", getattr(s, "fecha_vigencia", ""))

        c.drawString(60, y, f"ID: {s.id} | Carro ID: {carro_id} | Numero SOAT: {numero} | Vigencia: {fecha_vig}")
        y -= 15

    # Guardar el PDF
    c.save()
    buffer.seek(0)

    file_path = "reporte_detallado.pdf"
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="reporte_detallado.pdf",
    )
