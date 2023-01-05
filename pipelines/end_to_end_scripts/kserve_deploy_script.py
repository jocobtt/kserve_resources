from kserve import KServeClient
from kserve import InferenceService
from kserve import Model
import kfp
import kfp.compiler as compiler 
import kfp.dsl as dsl
from kfp import components
import os

# https://github.com/kserve/kserve/blob/master/docs/samples/pipelines/sample-custom-model.py

kserve_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/'
                                               'master/components/kserve/component.yaml')

@dsl.pipeline(
    name='kserve pipeline',
    description='A pipeline to deploy a kserve model.'
)

def kserve_pipeline(
    action = 'apply',
    model_name = 'boston_house',
    namespace = 'kserve-test',
    model_uri = 'https://github.com/jocobtt/kserve_resources/blob/main/sklearn/boston_model.joblib?raw=true',
    framework = 'sklearn'):
    kserve_op(action = action, model_name = model_name, namespace = namespace, 
    model_uri = model_uri, framework = framework)

if __name__ == '__main__':
    compiler.Compiler().compile(kserve_pipeline, 'kserve_pipeline.yaml')

    # Submit the pipeline to the client
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    client.create_experiment("kserve_pipeline")
    client.create_run_from_pipeline_func(kserve_pipeline, arguments = {}, experiment_name = "kserve_pipeline")    


"""
from kserve_client import Client

# Create a client object
client = Client()

# Create a new custom model
client.create(name="text_classifier", implementation={"framework": "custom", "model_uri": "gs://my-bucket/model/1"})

# Deploy the custom model
client.deploy(name="text_classifier")

# Make a prediction with the custom model
response = client.predict(name="text_classifier", data={"text": "this is some text to classify"})
print(response["category"])

"""