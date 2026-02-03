FROM python:3.10.12

COPY . /app
WORKDIR /app



RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "setup.py"]