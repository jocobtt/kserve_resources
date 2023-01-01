FROM python:3.8

# Copy requirements.txt into the container
COPY requirements.txt ./

# Install the numpy and pandas packages using pip
RUN pip install -r requirements.txt

COPY . . 