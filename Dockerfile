# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install cron and other necessary packages
RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements (if any) and install them
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY moca_info.py /app/moca_info.py

# Give execution permissions to the script
RUN chmod +x /app/moca_info.py

# Copy the crontab file to the cron.d directory
COPY crontab /etc/cron.d/moca_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/moca_cron

# Apply cron job
RUN crontab /etc/cron.d/moca_cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Set the entrypoint to run the cron daemon
CMD ["cron", "-f"]
