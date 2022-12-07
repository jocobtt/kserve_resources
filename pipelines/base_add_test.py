import kfp
from kfp import dsl
import os

@dsl.pipeline(
    name="Addition pipeline"
)
def add_pipeline(
    a: float,
    b: float
) -> float:
    # Define the pipeline steps
    step1 = dsl.ContainerOp(
        name="add_numbers",
        image="python:3.8",
        command=["python", "-c"],
        arguments=["print({} + {})".format(a, b)]
    )
    return step1.output



if __name__ == "__main__":
    kfp.compiler.Compiler().compile(add_pipeline, package_path ="add_pipe.yaml")

    # Submit the pipeline to the client
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    client.create_run_from_pipeline_func(add_pipeline, arguments={"a": 2.0, "b": 3.0}, experiment_name = "test")