FROM python:3.11-slim

WORKDIR /app
COPY app/ /app/         # Обрати внимание на слэш в конце
COPY requirements.txt ./
COPY run.sh /run.sh

RUN apt-get update \
 && apt-get install -y jq \
 && pip install --no-cache-dir -r requirements.txt \
 && chmod +x /run.sh

CMD [ "/run.sh" ]
