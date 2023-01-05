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
# add a part where we create the regex model here as well.. 
def regex_pipeline(
    action = 'apply',
    model_name = 'regex-model',
    namespace = 'kserve-test',
    custom_model_spec= '{"name": "regex-model", "image": "regex-image:latest", "port": "5000"}'):
    kserve_op(action = action, model_name = model_name, namespace = namespace, custom_model_spec = custom_model_spec)

if __name__ == '__main__':
    compiler.Compiler().compile(regex_pipeline, 'regex_pipeline.yaml')

    # Submit the pipeline to the client
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    client.create_experiment("kserve_pipeline")
    client.create_run_from_pipeline_func(regex_pipeline, arguments = {}, experiment_name = "kserve_pipeline")    
