FROM python:3.9.18-alpine3.18
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["sh", "entrypoint.sh"]