FROM python:3.11-buster

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .

EXPOSE 5000

ENTRYPOINT ["poetry", "run", "python", "src/main.py"]