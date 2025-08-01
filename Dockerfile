FROM python:3.11-slim

WORKDIR /app
COPY app /app
COPY requirements.txt ./
COPY run.sh /run.sh

RUN pip install --no-cache-dir -r requirements.txt \
 && chmod +x /run.sh

CMD [ "/run.sh" ]
