import kserve 
from kserve import KServeClient
import kfp
from kfp import dsl

kserve = KServeClient()

# Create a new inferenceservice
kserve.create_inference_service(
    name="my-custom-service",
    model_name="my-custom-model",
    model_path="path/to/my/model.py"
)

# Test the inferenceservice
kserve.test_inference_service(
    name="my-custom-service",
    input_data="" # our regex pattern goes here  
)

# Deploy the inferenceservice to a kubernetes cluster
kserve.deploy_inference_service(
    name="my-custom-service"
)

# Delete the inferenceservice when you no longer need it
#kserve.delete_inference_service(
#    name="my-custom-service"
#)