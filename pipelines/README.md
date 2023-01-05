# Pipelines 

This is the directory that will contain my examples for kubeflow pipelines. I am hoping to start tying in some of the concepts of pipelines with kserve so that we can better implement an end to end pipeline for our kubeflow cluster. 

## Key Lessons Learned

Some of the key lessons learned for this task revolve around how to submit work to the client. I haven't explored how to do so remotely (and I want to pull in work revolving this soon) but a big learning curve we overcame was revolved around how we create the poddefault definition for a given users namespace to connect to kubeflow pipelines client from the kubeflow notebook. We also learned how to create the rbac necessary to make this connection also. [doc here](https://www.kubeflow.org/docs/components/pipelines/v1/sdk/connect-api/). Overall the syntax is pretty nice. We essentially use the `kfp` python module to define our pipeline, our function that we want to input into our container, convert it into our yaml file, submit and execute our pipeline as a run in kubeflow. 

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

A few aspects that we will need to solidify is creating images for our specific usecases, how to make remote calls to our notebooks (will require us to figure out our load balancer configuration etc.), and a few more best practices for how we want to build out our pipelines. Also, better balancing out the use of custom images and how to build some from base images ad hoc. Then another thing is the different uses of the base pipelines, components, and partial commands. 