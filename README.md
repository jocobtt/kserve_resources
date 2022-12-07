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


MODEL_NAME=github-sklearn-model
INPUT_PATH=@./test_payload.json
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

kubectl post my-inference-service.default.svc.cluster.local:8080/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```


# Pretrained pytorch/huggingface model


# Pipelines 
