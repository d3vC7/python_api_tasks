# Prueba técnica task manager
A FastAPI-based RESTful API for managing tasks with MySQL database, containerized with Docker.

## Features
- operaciones CRUD para la entidad tarea.
- Integración con Mysql
- Uso de docker para manejo en contenedores.
- OpenAPI

### Tasks (Items)
- `GET /items` - List all tasks
- `GET /items/{id}` - Get a specific task
- `POST /items` - Create a new task
- `PUT /items/{id}` - Update a task
- `DELETE /items/{id}` - Delete a task


## Inicio rápido
1. **Clonar y navegador al directorio del proyecto
2. Ejecutar:
    docker-compose up --build

## Acceso a las apis
    API: http://localhost:8000
    Swagger UI: http://localhost:8000/docs

## Detener los contenedores.
    docker-compose down