FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/api/requirements.txt /tmp/requirements.txt
COPY packages/shared /tmp/packages/shared

RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /tmp/packages/shared

COPY apps/api /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
