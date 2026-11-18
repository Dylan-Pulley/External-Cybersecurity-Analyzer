FROM node:22-bookworm-slim AS frontend
WORKDIR /build/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --include=dev
COPY web/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# python-nmap needs the system executable and its service/probe data files.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nmap ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && nmap --version \
    && python -c "import nmap; print('Nmap executable:', nmap.PortScanner().nmap_version())"

COPY app.py main.py vulnerable_localhost.py ./
COPY port/ ./port/
COPY tls/ ./tls/
COPY config/ ./config/
COPY --from=frontend /build/web/dist ./web/dist

RUN useradd --create-home scanner
USER scanner
EXPOSE 10000
CMD ["sh", "-c", "exec python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]

# CI can check this stage without adding test dependencies to production.
FROM runtime AS verification
USER root
RUN python -m pip install --no-cache-dir httpx2
COPY tests/ ./tests/
USER scanner
RUN python -m unittest discover -s tests -v

FROM runtime AS production
