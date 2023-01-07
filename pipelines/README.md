# Pipelines 

This is the directory that will contain my examples for kubeflow pipelines. I am hoping to start tying in some of the concepts of pipelines with kserve so that we can better implement an end to end pipeline for our kubeflow cluster. 

## Key Lessons Learned

Some of the key lessons learned for this task revolve around how to submit work to the client. I haven't explored how to do so remotely (and I want to pull in work revolving this soon since this will prove useful for future workflows) but a big learning curve we overcame was revolved around how we create the `poddefault` definition for a given users namespace to connect to kubeflow pipelines client from the kubeflow notebook. We also learned how to create the rbac necessary to make this connection [doc here](https://www.kubeflow.org/docs/components/pipelines/v1/sdk/connect-api/). Overall the syntax is pretty nice. We essentially use the `kfp` python module to define our pipeline, our function that we want to input into our container, convert it into our yaml file, submit and execute our pipeline as a run in kubeflow. 

Our pod default manifest would look like the following: 
    
    ```yaml
apiVersion: kubeflow.org/v1alpha1
kind: PodDefault
metadata:
  name: access-ml-pipeline
  namespace: jacob-braswell
spec:
  desc: Allow access to Kubeflow Pipelines
  selector:
    matchLabels:
      access-ml-pipeline: "true"
  env:
    - ## this environment variable is automatically read by `kfp.Client()`
      ## this is the default value, but we show it here for clarity
      name: KF_PIPELINES_SA_TOKEN_PATH
      value: /var/run/secrets/kubeflow/pipelines/token
  volumes:
    - name: volume-kf-pipeline-token
      projected:
        sources:
          - serviceAccountToken:
              path: token
              expirationSeconds: 7200
              ## defined by the `TOKEN_REVIEW_AUDIENCE` environment variable on the `ml-pipeline` deployment
              audience: pipelines.kubeflow.org      
  volumeMounts:
    - mountPath: /var/run/secrets/kubeflow/pipelines
      name: volume-kf-pipeline-token
      readOnly: true
      ```

Now we have the pod default properly configured, when we are submitting our kubeflow pipelines within our cluster we can do the following:

```python
import os
import kfp

with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    #client.create_experiment("test")
    client.create_run_from_pipeline_func(pipeline_func, arguments={})
```



In this directory we have a few examples of pipelines that we can use and build on as guide posts for how we as a team want to build out our kubeflow pipelines to leverage within Kubeflow. 

A few aspects that we will need to solidify is creating images for our specific usecases, how to make remote calls to our notebooks (will require us to figure out our load balancer configuration etc.), and a few more best practices for how we want to build out our pipelines. Also, better balancing out the use of custom images and how to build some from base images ad hoc. We will also need to figure out how to use kubeflow pipelines with kserve this seems to be largely figured out but I am still needing to do some more testing for this.


#### Kserve client within a pipeline:
According to some documentation that I stumbled on there is a way to use the kserve client within a kubeflow pipeline. I am going to try and test this out and see if it works. I am hoping that this will allow us to leverage the kserve client to make calls to our kserve models within our pipeline. It looks something like this: 

```python


```


## Pipelines vs Components for kubeflow pipelines:

Within Kubeflow pipelines SDK there are two main types of functions that you can call, pipelines and components. They are the main building blocks leveraged for making your kubeflow pipeline work and incorporate the different inputs and functions that are desired. I am wanting to spend a little time talking through the two and maybe highlighting their differences and use-cases. 

Pipelines are the main function that you will use to define your pipeline. A pipeline is a portable and scalable defintion of a ML workflow with each step laid out for it. Each step in the workflow makes up an instance of the pipeline component. For instance preparing the data, training the model, testing the model, or any other ml workflow step would fit within our pipeline. You define your pipeline by specifiying the pipeline's metadata, including the name and description, and the list of the pipeline's arguments and their types. You can also define the pipeline's inputs and outputs. Then you define the pipeline's tasks, which are the individual steps in the workflow. Each task is an instance of a pipeline component. You can also define the conditions under which the tasks run.

Below is a simple example of a pipeline that adds two elements together. 

```python
from kfp import dsl
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
```

A component is a self-contained set of code that performs one step in your ML workflow. It is made up of a containerized program, it's dependencies, and the interface for passing data to and from the component. You define a component in a component specification. 

Some best practices for components are to make them as small as possible, and to make them reusable. Reuse components to avoid duplicating code. Also components should be self-contained and have all the dependencies they need to run and have a single responsibility. This helps it easier to test, reuse, and maintain. Data is passed between components using file paths. The component specification defines the interface for passing data to and from the component. The component specification also defines the component's inputs and outputs.

Below is an example of a component that adds two numbers together.

```python
from kfp import dsl 
@dsl.component
def add(a: float, b: float) -> float:
   '''Calculates sum of two arguments'''
   return a + b

# then we would later submit this component to our pipeline like so 
@dsl.pipeline(
    name="Addition pipeline"
)
def add_pipeline(
    a: float,
    b: float
) -> float:
    # Define the pipeline steps
    step1 = add(a, b)
    return step1.output
```

More information about these two concepts can be found [here](https://www.kubeflow.org/docs/components/pipelines/v1/sdk/build-pipeline/).

