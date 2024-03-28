FROM python:3.9

WORKDIR /app

RUN pip install --upgrade pip
COPY /backend/requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
