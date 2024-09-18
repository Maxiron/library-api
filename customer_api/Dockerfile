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
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
