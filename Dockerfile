FROM python:3.11-slim
EXPOSE 8000
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh scripts/wait_until_migrations_entrypoint.sh
ENTRYPOINT ["bash", "scripts/entrypoint.sh"]