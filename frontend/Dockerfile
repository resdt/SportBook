# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app/frontend

# Copy application code
COPY . /app/frontend

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will use
EXPOSE 8501

# Define the command to run the application
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
