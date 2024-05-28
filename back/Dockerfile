# Use an official Python runtime as a parent image
FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN apt-get update && apt-get install -y netcat-openbsd
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install channels==4.0.0
RUN pip install daphne==4.0.0
COPY . /code/
COPY ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/code/entrypoint.sh"]
