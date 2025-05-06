# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "localhost:5000", "app:app", "--workers", "2"]
