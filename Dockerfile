
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN chmod +x run.sh && pip install --no-cache-dir -r requirements.txt

CMD ["./run.sh"]
