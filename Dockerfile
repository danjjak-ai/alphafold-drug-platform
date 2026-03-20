# Use python 3.10-slim as base
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy requirement files and install
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Download AutoDock Vina binary for Linux
RUN mkdir -p vina_bin/linux && \
    wget https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O vina_bin/linux/vina && \
    chmod +x vina_bin/linux/vina

# Copy project files
COPY . .

# Run JS injection to prepare frontend assets
RUN python web/inject_js.py

# Seed demo data into the database at build time
# This ensures Cloud Run has data without requiring the full pipeline
RUN mkdir -p data && python scripts/seed_demo_data.py

# Expose Streamlit port
EXPOSE 8080

# Run Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "web/app.py"]
