FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos de la aplicación
COPY app/ ./app/
COPY database/ ./database/
COPY schemas/ ./schemas/
COPY SQL/ ./SQL/

# Copiar archivo principal de la aplicación
COPY main.py .

# Establecer variables de entorno
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación con espera para MySQL
CMD ["sh", "-c", "sleep 15 && python main.py"]