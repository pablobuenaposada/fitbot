FROM python:3.13

ENV PYTHONPATH=src
WORKDIR /app

COPY src /app/src
COPY Makefile pyproject.toml /app/

RUN pip install uv

CMD ["make", "run"]