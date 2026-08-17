FROM python:3.12.13-slim-bookworm

# 2. Configura variables para que Python sea rápido en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. EQUIVALENTE A TU CONDA: Instala las librerías espaciales del sistema operativo
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 4. Le dice a GeoDjango exactamente dónde encontrar GDAL en este Linux
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV PROJ_LIB=/usr/share/proj/

# 5. Crea la carpeta de la tesis dentro del contenedor
WORKDIR /app

# 6. Instala las librerías de Python (Django, Altair, etc.)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copia tu código actual
COPY . /app/