FROM python:3.8

# Copy the pipeline code into the container
COPY . .

# Install the numpy and pandas packages using pip
#RUN pip install -r requirements.txt

CMD ["python", "regex_serve.py"]