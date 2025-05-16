FROM python:3.11-slim

ENV http_proxy=http://10.170.250.80:8080
ENV https_proxy=http://10.170.250.80:8080

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

CMD ["flask", "run"]
