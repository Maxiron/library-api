# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Update the package list and install mysqlclient dependencies
RUN apt-get update && apt-get install -y default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    pkg-config \
    libpq-dev \ 
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY admin_api/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY admin_api/entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy the current directory contents into the container at /app
COPY admin_api /app

RUN chmod +x entrypoint.sh

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Run main.py when the container launches
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
ENTRYPOINT ["./entrypoint.sh"]
