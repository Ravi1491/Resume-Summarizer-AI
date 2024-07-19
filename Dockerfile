# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ARG GROQ_API_KEY
ENV GROQ_API_KEY=$GROQ_API_KEY
ENV FLASK_APP=run.py
ENV CONFIG_MODE=production

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]