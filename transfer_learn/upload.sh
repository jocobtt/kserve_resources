#!/bin/bash
PROJ=jacob-dev-345806
BUCK=kserve_modelz
gcloud alpha storage cp boston_model.joblib gs://${BUCK}/pretrained --project ${PROJ}
