ARG PYTHON_VER=3.11

FROM python:${PYTHON_VER} AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install Poetry (uncomment if you want to use Poetry)
# RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry && \
#     poetry config virtualenvs.create false

# COPY ./pyproject.toml ./poetry.lock* /app/
# RUN poetry install --no-root

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

FROM python:${PYTHON_VER}-slim

WORKDIR /app

COPY --from=base /app /app

# Install runtime dependencies in the final image
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "3000"]
