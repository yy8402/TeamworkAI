# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run service.py when the container launches
CMD ["python", "service.py"]