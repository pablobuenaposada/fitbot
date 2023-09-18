FROM python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /usr/src/app/
ENTRYPOINT [ "python", "./main.py" ]