FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server.py /app/server.py

EXPOSE 8080

CMD ["python", "server.py"]


