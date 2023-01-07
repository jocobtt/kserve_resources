FROM python:3.8

ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the pipeline code into the container
COPY requirements.txt ./

COPY regex_func.py ./

COPY regex_dump.pkl ./

COPY regex_serve.py ./

# Install our libraries 
RUN pip install -r requirements.txt

CMD ["python", "regex_serve.py"]