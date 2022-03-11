FROM python:latest

WORKDIR /usr/src/app

COPY src /usr/src/app/src
COPY Makefile requirements.txt requirements-tests.txt setup.cfg /usr/src/app/

RUN make venv

CMD ["make", "run"]