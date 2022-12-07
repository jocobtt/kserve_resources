#!/bin/bash
PROJ=jacob-dev-345806
BUCK=kserve_modelz
gcloud alpha storage cp boston_model.joblib gs://${BUCK}/sklearn --project ${PROJ}

# if uploading to s3 we can do this instead - then we will need to attempt a different method for using this bucket inside our kfserve inference service - 
# aws s3 cp boston_model.joblib s3://${BUCK}/sklearn --profile ${PROJ}

