FROM python:3.12
WORKDIR /app
COPY collect_data.py .
RUN pip install requests prometheus-client pandas
CMD ["python", "collect_data.py"]