# Use Python 3.12
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port the app will use
EXPOSE 3000

# Define the command to run the application
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "3000"]
