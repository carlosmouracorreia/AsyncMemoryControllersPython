FROM python:3.11-slim

USER root

WORKDIR /app

RUN pip install docker flask

COPY exporter.py .

CMD ["python", "exporter.py"]