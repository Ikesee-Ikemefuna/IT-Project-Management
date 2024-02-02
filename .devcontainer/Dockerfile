FROM python:3.8

WORKDIR /workspace

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Flask app port
EXPOSE 5000

# Copy the entire project into the container
COPY . .

# Run the Flask app
CMD ["python", "main.py"]
