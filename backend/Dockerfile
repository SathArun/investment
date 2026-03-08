FROM python:3.11-slim

# Install system dependencies for SciPy and Meson
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser /app && chmod +x entrypoint.sh
USER appuser

EXPOSE 8000
CMD ["bash", "entrypoint.sh"]
