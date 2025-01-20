# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app/backend

# Copy application code
COPY . /app/backend

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will use
EXPOSE 8080

# Define the command to run the application
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8080", "--reload"]
