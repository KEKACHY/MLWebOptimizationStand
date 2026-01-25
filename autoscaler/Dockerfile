FROM python:3.12
WORKDIR /app
COPY scale.py .
RUN pip install docker requests
CMD ["python", "scale.py"]