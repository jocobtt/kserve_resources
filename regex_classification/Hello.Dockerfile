FROM python:3.8

ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the pipeline code into the container
#COPY requirements.txt ./

COPY requirements.txt ./

COPY hello_world.py ./

COPY hello_world.pkl ./

COPY hello_world_serve.py ./

# Install the numpy and pandas packages using pip
RUN pip install -r requirements.txt

CMD ["python", "hello_world_serve.py"]



