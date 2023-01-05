import kfp
from kfp import dsl
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from joblib import dump
from sklearn.datasets import load_boston
import pandas as pd
import os

@dsl.pipeline(
    name="sklearn pipeline"
)
def sklearn_pipeline():
    # Define the pipeline steps
    step1 = dsl.ContainerOp(
        name="load_boston",
        image="python:3.8",
        command=["python", "-c"],
        arguments=["import pandas as pd; from sklearn.model_selection import train_test_split; from sklearn.tree import DecisionTreeRegressor \
                from joblib import dump; from sklearn.datasets import load_boston; boston_df = load_boston(); \
                boston = pd.DataFrame(boston_df.data, columns=boston_df.feature_names); \
                X=boston.iloc[:,0:-1]; y=boston.iloc[:,-1]; X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42); \
                regressor = DecisionTreeRegressor(random_state=42, max_depth=5); regressor.fit(X_train, y_train); dump(regressor, 'boston_model.joblib')"] # output needs to be the model stuff though
    )
    # step two deploys our inference service from above 
    step2 = dsl.ContainerOp(
        name = "serve_model",
        image = "python:3.8",
        command = ["python", "kserve_inference.py"], # need to load this python file
        #arguments = [""]
    )


if __name__ == "__main__":
    kfp.compiler.Compiler().compile(sklearn_pipeline, package_path ="sklearn_pipe.yaml")

    # Submit the pipeline to the client
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        TOKEN = f.read()

    client = kfp.Client(
        host='http://ml-pipeline.kubeflow.svc.cluster.local:8888',
        existing_token=TOKEN)
    # create our experiment 
    client.create_run_from_pipeline_func(sklearn_pipeline, experiment_name = "test")