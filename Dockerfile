FROM python:3.9.0-slim-buster

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && \
    apt-get install --no-install-recommends -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "bot.py"]
