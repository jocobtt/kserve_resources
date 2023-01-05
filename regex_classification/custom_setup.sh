# following these steps and documenting as I go - https://kserve.github.io/website/0.9/modelserving/v1beta1/custom/custom_model/
#!/bin/bash

# install pack cli  to build custom model server image 
brew install buildpacks/tap/pack

# https://github.com/kserve/kserve/blob/master/python/custom_model/model.py

# creating our custom model server 
pack build --builder=heroku/buildpacks:20 ${DOCKER_USER}/hello-world:v1
docker push ${DOCKER_USER}/hello-world:v1

# test this out through docker 
docker run -ePORT=8080 -p8080:8080 ${DOCKER_USER}/hello-world:v1

curl localhost:8080/v1/models/hello-world:predict -d @./input.json
{"predictions": [[14.861763000488281, 13.94291877746582, 13.924378395080566, 12.182709693908691, 12.00634765625]]}


# now can apply the yaml we have for the inference service 