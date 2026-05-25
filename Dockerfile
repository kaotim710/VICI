FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY frontend ./frontend
COPY fixtures ./fixtures
COPY reports ./reports

RUN pip install --no-cache-dir .

ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python3", "scripts/run_web_ui.py"]
