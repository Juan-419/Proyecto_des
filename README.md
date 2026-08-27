URL: https://taller-de-carros.onrender.com


📌 README — Sistema de Gestión para Taller Automotriz – AutoFix Pro

🚗 Descripción del proyecto

AutoFix Pro es un sistema web desarrollado con FastAPI + SQLModel + Supabase + Jinja2
el cual permite gestionar la operación de un taller automotriz de forma eficiente.

✔ Registro y administración de clientes

✔ Control de carros vinculados a cada cliente

✔ Administración de mecánicos

✔ Registro de reparaciones con asignación de mecánicos

✔ Reportes dinámicos

✔ Panel Dashboard con métricas generales

✔ Carga de imágenes con Supabase Storage

✔ Sistema de eliminación lógica (active = False)

Este proyecto fue construido con enfoque académico y escalable para implementaciones reales.

🛠️ Tecnologías utilizadas
ComponenteTecnologíaBackendFastAPIBase de datosSQLModel + SQLite / Supabase StorageRender de plantillas HTMLJinja2ORM y relacionesSQLModel (relaciones 1:1, 1:N, N:M)UIBootstrap 5DeployRender.com⚙️ Funcionalidades principales

👥 Gestión de Clientes
Registro / edición / eliminación lógica
Almacenamiento de foto en Supabase
Listado + eliminados

🚗 Gestión de Vehículos
Relacionado con un cliente
Eliminación lógica
Listado dinámico

🔧 Gestión de Mecánicos
Registro, edición, eliminación
Relación N:M con reparaciones

🛠 Reparaciones
Registro de reparaciones
Selección de mecánicos asociados
Vistas HTML y API

📊 Dashboard
Conteo dinámico:

▪ Clientes

▪ Carros

▪ Mecánicos

▪ Reparaciones activas

📌 Arquitectura del proyecto
📦 app/
 ┣ 📁 templates/
 ┃ ┣ navbar.html
 ┃ ┣ header.html
 ┃ ┣ dashboard.html
 ┃ ┣ cliente_list.html
 ┃ ┣ carro_list.html
 ┃ ┣ mecanico_list.html
 ┃ ┣ reparacion_new.html
 ┃ ┗ ...
 ┣ 📁 supa/
 ┃ ┗ supabase_upload.py
 ┣ db.py
 ┣ main.py
 ┣ models.py
 ┣ cliente.py
 ┣ carro.py
 ┣ mecanico.py
 ┣ reparacion.py
 ┣ dashboard.py
 ┣ soat.py
 ┗ reporte.py
 
🗄️ Modelo de Base de Datos

Relaciones principales:
✔ Cliente 1:N Carro

✔ Carro 1:1 SOAT

✔ Carro 1:N Reparacion

✔ Reparacion N:M Mecánico

Modelo destacado:
class Reparacion(ReparacionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    carro_id: Optional[int] = Field(default=None, foreign_key="carro.id", nullable=True)
    active: bool = Field(default=True)
    carro: Optional[Carro] = Relationship(back_populates="reparaciones")
    mecanicos: List[Mecanico] = Relationship(back_populates="reparaciones", link_model=ReparacionMecanicoLink)
    
🚀 Instalación y Ejecución de forma local

📌 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux
venv\Scripts\activate      # Windows

📌 2. Instalar dependencias
pip install fastapi sqlmodel uvicorn jinja2 supabase-python python-multipart

📌 3. Ejecutar servidor
uvicorn main:app --reload


🚀 Ingreso web


🌐 Rutas principales
RutaDescripción/Página de inicio/clientes/Gestión de clientes/carros/Gestión de vehículos/mecanicos/Gestión de mecánicos/reparaciones/Registro de reparaciones/dashboard/Panel administrativo🧠 Dashboard

Ejemplo de métricas capturadas:

total_clientes = len(session.exec(select(Cliente)).all())
total_carros = len(session.exec(select(Carro)).all())
total_mecanicos = len(session.exec(select(Mecanico)).all())
reparaciones_activas = len(session.exec(select(Reparacion).where(Reparacion.active == True)).all())


📌 Supabase Storage

El sistema permite subir imágenes de usuarios o vehículos al bucket configurado:
✔ Conexión via supabase_client

✔ Guardado en Bucket público

✔ Se almacena el link de acceso en la BD


📌 Estado del proyecto

✔ Funcional

✔ Escalable a módulos como facturación, inventario o citas


✨ Contribuciones

Puede extenderse fácilmente:

API móvil

👨‍💻 Autor
Juan David Vega Alfonso

Estudiante de Ingeniería de Sistemas

Proyecto académico — Taller Automotriz AutoFix Pro
