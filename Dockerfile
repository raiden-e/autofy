FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

# config.py is never baked into the image — mount it at runtime via /config
RUN rm -f config.py

ENTRYPOINT ["./entrypoint.sh"]
