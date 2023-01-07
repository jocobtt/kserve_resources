This repo is testing out the feature to pull a model from github to then be deployed via kserve within a kubeflow cluster.

sklearn directory contains model resources for sklearn model. The model is trained on the iris dataset and is used for testing the kserve deployment.

Readme will contain instructions as well - still wip. 

Pre-trained model directory is work in progress. 
I am going to use google colab for this since I don't have access to my own gpu. But will leverage huggingface for loading my pretrained model. 

We essetentially have two options for this, can either run and build our models locally or run the models through kubeflow notebooks. I am hoping to try both of these options. 

# Sklearn model

The main thing we are wanting is to create a model and then store that model in a format that can be used by kserve. So for sklearn we can leverage the joblib library to save our model, like so: 

```python
from joblib import dump
dump(model, 'model.joblib')
```

We have a few options for endpoints that we can use for our storageURI. For the purpose of this exercise I am simply going to use github and google cloud storage. The github example is referring to this very repo, which is a public repo so we don't have to worry about permissions or anything like that. For google cloud storage we will need to create a bucket and then upload our model to that bucket and then create a service account to allow us to pull the model down into our inference service. We reference that service account name in our yaml manifest as seen in the `gcp_boston_infernece_service.yaml` file.

Once we have deployed our manifest. We can then follow these instructions to make an inference request: 

```bash
SERVICE_HOSTNAME=$(kubectl get inferenceservice github-sklearn-model -n kserve-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)

# if we are using a load balancer - INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}') 
# if we are using a nodeport - INGRESS_HOST=$(kubectl get node -o jsonpath='{.items[0].status.addresses[0].address}')
#INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')

# if port forwarding - our case
# in a separate terminal run - INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')
# kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80

# in a different terminal run the below 
export INGRESS_HOST=localhost
export INGRESS_PORT=8080
MODEL_NAME=github-sklearn-model
INPUT_PATH=@./test_payload.json
# curl -v http://sklearn-iris.kserve-test/v1/models/sklearn-iris:predict -d @./iris-input.json

curl -v http://${INGRESS_HOST}:${INGRESS_PORT}/v2/models/$MODEL_NAME:predict -d $INPUT_PATH


MODEL_NAME=github-sklearn-model
SESSION=MTY3MjkzNDM0NXxOd3dBTkZjMFRVbFRNMVZKVjBJeVJsQlNTa1ZLU2twSVJGRlNNbEpHVUV0SFQxWTJORFJTV1VOYVIxbERTRTFIU2taU04xVlNWVkU9fKiroToOojIHZqEmksewcy0L6Qr4WTlYSU_Ojj61o1lh
INPUT_PATH=@./test_payload.json
CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.clusterIP}')
SERVICE_HOSTNAME=$(kubectl get -n kserve-test inferenceservice ${MODEL_NAME} -o jsonpath='{.status.url}' | cut -d "/" -f 3)

# is the service ready? 
curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Cookie: authservice_session=${SESSION}" http://${CLUSTER_IP}/v2/models/${MODEL_NAME}

curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Cookie: authservice_session=${SESSION}" http://${CLUSTER_IP}/v2/models/${MODEL_NAME} -d ${INPUT_PATH}

```
Can also potentially use the kserve command line tool to make requests - ie kserve predict to predict and kserve list to list the models that we have available. 

For our usecase currently we don't have an external load balancer, so we handle the inferencing servicing via port forwarding but we will have to eventually move to using a load balancer for this aspect for our Collibrain Next implementation. We will also need to figure out what this looks like in the chi a bit better. 

# Pretrained pytorch/huggingface model
Still in the process of using hugging face/pytorch combination to train this model on google collab. 


# Custom model server work 
Essentially what you need is a container image that contains your model and a python script that will load your model and then serve it using the kserve python sdk. I reference this same concept below in the python function section below. But in this case instead of doing a hello world function or a regex function we are wanting to load a pretrained model and then serve it. 

# Questions from Nick
# auto redeploy inferencing service if there is a new storage uri - look into this if there - 3rd (see if something is out of the box)
  - kserve supports canary updates for model versions, which isn't entirely an automated process. https://github.com/kserve/kserve/issues/772
  - Seems like they are expecting a user to use gitops or some other framework for updating their model uris on that end of things but not from the kserve inferencing itself. 
  - if we connect our kserve deploying of the models through a kubeflow pipelines that can handle updating the model uri's for us.

# eventually want to call this all from jenkins to kick off the pipeline and then create the model etc. so will need to finalize connecting to the kubeflow client remotely. 
# how does it support multitenancy? 
 - it does appear to support multi-tenancy - https://www.bloomberg.com/company/stories/the-journey-to-build-bloombergs-ml-inference-platform-using-kserve-formerly-kfserving/
 - It appears that multi-tenancy is handled through the knative eventing multi-tenant broker -  https://kserve.github.io/website/0.9/modelserving/logger/logger/#create-an-inferenceservice-with-logger_1 - read more into this.. *
 - https://github.com/knative/serving/issues/12533

# how to deploy a simple python function - no specific ml framework in mind - 2nd 
  # (hello world, and through regex do classification). A lookup in elastic search for nearest neighbors (maybe). 
  There are a few ways to accomplish this. Essentially we are wanting to utilize the custom runtime. We can build this through the kserve cli or through the kserve python sdk. An example of how to do this is located in the `regex_classification` folder in this repo. We then will associate a docker image with this custom runtime and to do this we will need to build a docker image and push it to a docker registry. The docker image will essentially contain our pickled python function and a python script that will load this pickled function and use it to predict with that function. Like so:

  ```python
import kserve 
from typing import Dict, list
import pickle

class hello_world(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()
        self.model = None
        self.ready = False

    def load(self):
        # Load your model here
        self.model = pickle.load(open("hello_world.pkl", 'rb')) 
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        print('predict function called', request)
        inputs = request["inputs"]
        result = hello_world(inputs)
        return {"message": result}

if __name__ == "__main__":
    model = hello_world("hello-world")
    model.load()
    kserve.ModelServer().start([model])
  ```
  We can then use this docker image in our kserve inference service yaml file or through the kubeflow pipeline python client like so:

  ```python
import kfp.dsl as dsl
from kfp import components
kserve_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/'
                                               'master/components/kserve/component.yaml')
@dsl.pipeline(
    name='kserve pipeline',
    description='A pipeline to deploy a kserve model.'
)
def regex_pipeline(
    action = 'apply',
    model_name = 'regex-model',
    namespace = 'kserve-test',
    custom_model_spec= '{"name": "regex-model", "image": "regex-image:latest", "port": "5000"}'):
    kserve_op(action = action, model_name = model_name, namespace = namespace, custom_model_spec = custom_model_spec)
  ```
 Doc located here - https://kserve.github.io/website/modelserving/v1beta1/custom/custom_model/

 Some issues that I am currently dealing with it is that the cluster has insufficient cpu for running two custom models. The custom model pods themselves arent' that large necessarily so I am hoping that this isn't an issue with kubeflow serving too many kserve pods/models at once from a resource perspective.

# performance testing - k6 related stuff etc
- There are a few ways we can accomplish this ie through k6, locust, or even just using the kserve command line tool.
- https://github.com/kserve/kserve/blob/master/docs/samples/v1beta1/sklearn/v1/perf.yaml
- https://github.com/kserve/modelmesh-performance/tree/main/k6_test

# rest api automation etc.

# monitoring (related to multitenancy part) - how does it hook into promethues/grafana. - 5th
#   - What are the metrics that it is exposing?
#   - Is it assuming single tenant model vs multi tenant model? 

https://github.com/kserve/kserve/tree/master/docs/samples/metrics-and-monitoring





This is where I will keep my notes for kserve as I make my various tests. I will try to first do a simple sklearn model and then collaborate with Nick to do a pretrained model. 

I will try and document the things I run into and learn that I think will be useful for others. 

Essentially need a few different things to get started:
- first a model (in our case we are going to use a sklearn model and a pretrained model). We are going to use our kubeflow pipeline to train the model and then create our storage object to store the model in. (This in theory should just rely on the same object store that our kubeflow pipeline uses).
- If we are using a custom runtime, Ie for running a simple python function. We will need to create a container image to go along with our custom runtime.
- a inference service manifest file that defines the model and the container image. Within this manifest we define the storage uri for our model, can make requests for the amount of storage that we want associated with the model, the number of replicas we want associated with the model, gpu access for the model, autoscaling configurations, and many other things. 
- a curl request to test the model inferencing endpoint. 

Can performance test our model using this - kubectl create -f https://raw.githubusercontent.com/kserve/kserve/release-0.8/docs/samples/v1beta1/sklearn/v1/perf.yaml -n kserve-test


For pretrained models - https://thenewstack.io/serve-tensorflow-models-with-kserve-on-google-kubernetes-engine/
custom - http://www.pattersonconsultingtn.com/blog/deploying_huggingface_with_kfserving.html 

look at batch prediction as well - https://github.com/kserve/kserve/tree/master/docs/samples/batcher

auto scaling also - https://github.com/kserve/kserve/tree/master/docs/samples/autoscaling

explaining - https://github.com/kserve/kserve/tree/master/docs/samples/explanation

Is there any way to automate uploading our model image to our storageuri? 
Can also upload/use model uri from github - https://kserve.github.io/website/0.8/modelserving/storage/uri/uri/#tensorflow 
pvc - https://kserve.github.io/website/0.8/modelserving/storage/pvc/pvc/, s3, or azure 

This is for showcasing how to do sklearn from scratch - https://github.com/kserve/kserve/tree/master/docs/samples/v1beta1/sklearn/v1#run-sklearn-inferenceservice-with-your-own-image

https://medium.com/@angusll/deploying-an-deep-learning-model-using-kserve-and-google-cloud-vertex-ai-ae2850caf27 * 

https://github.com/alexeygrigorev/kubeflow-deep-learning *
Especially here - https://github.com/alexeygrigorev/kubeflow-deep-learning - will maybe jjust need to use a script to push resources to s3/gcs once they are created then..?

# knative notes 
https://knative.dev/docs/developer/serving/services/creating-services/ - this is the link to the knative docs for creating services.


# Relationship between experiments and pipelines
The following are my notes from DEV-29731.
 
Kubeflow pipelines are a way to orchestrate our machine learning workflows. Pipelines are made up of steps that are executed in order. Each step is a containerized component. These pipelines can be run using a kubeflow run. The run is the execution of the pipeline and is associated with a pipeline version. This allows us to track the different versions of our pipeline, compare them, and rerun them. Each run is associated with an experiment. The experiment is a logical grouping of our runs.
 
We can have multiple pipelines attributed to an experiment. A pipeline can also not be associated with an experiment. But it appears that if we want to submit a pipeline to a run it is best practice to have it associated with an experiment.
 
Conceptually, an experiment is where you can try different configurations of your pipelines. Experiments can also be used to organize our runs into logical groups. This is particularly useful for different hyperparameter tuning runs or training different model versions in your pipeline.
 
We can create and connect our runs to an experiment through the kubeflow UI. We can also do this through the kubeflow client. The client method provides us with more flexibility and control. Below is an example of how we can associate a run to an experiment.
 
```python
client = kfp.Client(
       host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
       existing_token=TOKEN)
client.create_experiment("test")
client.create_run_from_pipeline_func(add_pipeline, arguments={"a": 2.0, "b": 3.0}, experiment_name = "test")
```
 
If we submit a run without associating it to an experiment then it will be associated with the default experiment. If we are executing runs through the UI then we can associate them to an experiment through the UI.
 
For versioning for the pipelines, each time we submit a pipeline to a run that run is assigned a version. This run is connected to the experiment so its generated version is essentially the date that the run was submitted and the name of the pipeline. Ie if we inspected a run that happened on 2022-12-07 00-21-39 then we would expect the version to be the name of the pipeline and the date that the pipeline was executed. This allows us to track the different versions of our pipeline.




# image notes 
For Kubeflow notebooks, or any python work we do in kubeflow really, we have a few options for creating our images. We can use the base image that is provided by kubeflow, we can use the base image that is provided by google, or we can use our own custom image. In terms of image that are available in AWS we have the following images located in this [link](https://github.com/aws/deep-learning-containers/blob/master/available_images.md). So essentially pytorch, tensorflow, mxnet, and chainer. These images also have the following packages installed on them as well: 
  - kfp
  - kfserving
  - h5py
  - pandas
  - awscli
  - boto3
