import kfp
from kfp import dsl
import pandas as pd 
import psycopg2
import os

@dsl.pipeline(
    name="Redshift data pipeline",
    description="A pipeline to pull data from Redshift using awswrangler",
)
def redshift_pipeline():
    # Define the pipeline steps
    step1 = dsl.ContainerOp(
        name="pull_data_from_redshift",
        image="jacobkun/red_etl:alpha",
        command=["python"],
        arguments=[
            "-c",
            "import pandas as pd; import psycopg2; \
            conn = psycopg2.connect(host=,user=, \
            port=5439, password=,dbname= 'master'); df = pd.read_sql_query('SELECT * FROM collibrain_dataclassification.labels', conn); df = df.dropna(); print(df.head())"
        ]
    )

if __name__ == "__main__":
    kfp.compiler.Compiler().compile(redshift_pipeline, "data_read.yaml")

    # Submit the pipeline to the client
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    # client.create_experiment("redshift_etl_test")
    client.create_run_from_pipeline_func(redshift_pipeline, arguments = {}, experiment_name = "redshift_etl_test")
