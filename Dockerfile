FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY uv.lock pyproject.toml ./ 

RUN pip install uv && uv sync

COPY . .

EXPOSE 8000

CMD ["uv", "run", "main.py"]
