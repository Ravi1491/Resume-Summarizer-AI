# Use an official Python runtime as the base image
FROM python:3.12-alpine

EXPOSE 5000/tcp

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

# Run the application
CMD ["python", "app.py"]
