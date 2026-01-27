FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

COPY main.py /app/main.py

CMD ["python", "main.py"]