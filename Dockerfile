FROM python:3.12-slim

WORKDIR /app

COPY prod_report_bot.py .

RUN pip install --no-cache-dir python-telegram-bot matplotlib

CMD ["python", "prod_report_bot.py"]
