# ============================================================================
# DOCKERFILE - BolsaV1 Sistema de Gestão de Valores Cotizados v2.0.0
# ============================================================================

# Usar imagen base de Python 3.12 slim
FROM python:3.12-slim

# Metadata de la imagen
LABEL maintainer="BolsaV1 Development Team"
LABEL description="Sistema de Gestão de Valores Cotizados - Arquitectura Modular"
LABEL version="2.0.0"

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Crear usuario no-root para mayor seguridad
RUN groupadd -r bolsa && useradd -r -g bolsa -s /bin/bash bolsa

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación modular
COPY main.py .
COPY app/ ./app/
COPY .env.docker .env

# Crear directorios necesarios con permisos correctos
RUN mkdir -p logs exports backups && \
    chown -R bolsa:bolsa /app && \
    chmod -R 755 /app

# Cambiar a usuario no-root
USER bolsa

# Asegurar que los directorios sean escribibles después del cambio de usuario
RUN mkdir -p logs exports backups && \
    touch logs/.gitkeep exports/.gitkeep backups/.gitkeep

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando de inicio con la nueva estructura modular
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]