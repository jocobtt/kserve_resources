#!/bin/bash
LOC=jacob-dev-4333
BUCK=bucket-name
gcloud storage cp boston_model.joblib gs://${LOC}/${BUCK}

