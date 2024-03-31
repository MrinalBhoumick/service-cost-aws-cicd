# Use the official Python image as base
FROM python:3.9
# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000
# Set working directory in the container
WORKDIR /app
# Copy the requirements file to the container
COPY requirements.txt requirements.txt
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the Flask application code to the container
COPY . .
# Expose the Flask port
EXPOSE 5000
# Command to run the Flask application
CMD ["flask", "run"]