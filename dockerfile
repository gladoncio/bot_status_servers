# Use the official Python image as base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your bot when the container starts
CMD ["python", "main.py"]
