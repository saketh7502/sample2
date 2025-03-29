FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir flask
RUN pip install bootstrap-flask

# Create directory for databases
RUN mkdir -p /app/database

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Set default environment variable
ENV TREATMENT=false

EXPOSE 8080

# Define entrypoint script to handle arguments
ENTRYPOINT ["python", "app.py"]

# Default command (can be overridden)
CMD []
