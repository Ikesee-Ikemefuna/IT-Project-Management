# Use the official Python base image with Alpine Linux
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev git

# Install Flask and Gunicorn
RUN pip install --no-cache-dir Flask==2.0.1 Werkzeug==2.0.3 gunicorn==20.1.0 apiflask==2.1.0 requests==2.26.0 flask-mysqldb==0.2.0

# Copy the entire project to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Python application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
