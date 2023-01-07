#https://github.com/kubeflow/kfp-tekton/blob/master/samples/e2e-mnist/mnist.ipynb
import kfp
import kfp.dsl as dsl
from kfp import components
from kubeflow import katib
def create_katib_experiment_task(experiment_name, experiment_namespace, training_steps):
    # Trial count specification.
    max_trial_count = 5
    max_failed_trial_count = 3
    parallel_trial_count = 2

    # Objective specification.
    objective = katib.V1beta1ObjectiveSpec(
        type="minimize",
        goal=0.001,
        objective_metric_name="loss"
    )

    # Algorithm specification.
    algorithm = katib.V1beta1AlgorithmSpec(
        algorithm_name="random",
    )

    # Experiment search space.
    # In this example we tune learning rate and batch size.
    parameters = [
        katib.V1beta1ParameterSpec(
            name="learning_rate",
            parameter_type="double",
            feasible_space=katib.V1beta1FeasibleSpace(
                min="0.01",
                max="0.05"
            ),
        ),
        katib.V1beta1ParameterSpec(
            name="batch_size",
            parameter_type="int",
            feasible_space=katib.V1beta1FeasibleSpace(
                min="80",
                max="100"
            ),
        )
    ]

    # Experiment Trial template.
    # TODO (andreyvelich): Use community image for the mnist example.
    trial_spec = {
        "apiVersion": "kubeflow.org/v1",
        "kind": "TFJob",
        "spec": {
            "tfReplicaSpecs": {
                "Chief": {
                    "replicas": 1,
                    "restartPolicy": "OnFailure",
                    "template": {
                        "metadata": {
                            "annotations": {
                                "sidecar.istio.io/inject": "false"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "tensorflow",
                                    "image": "docker.io/liuhougangxa/tf-estimator-mnist",
                                    "command": [
                                        "python",
                                        "/opt/model.py",
                                        "--tf-train-steps=" + str(training_steps),
                                        "--tf-learning-rate=${trialParameters.learningRate}",
                                        "--tf-batch-size=${trialParameters.batchSize}"
                                    ]
                                }
                            ]
                        }
                    }
                },
                "Worker": {
                    "replicas": 1,
                    "restartPolicy": "OnFailure",
                    "template": {
                        "metadata": {
                            "annotations": {
                                "sidecar.istio.io/inject": "false"
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "tensorflow",
                                    "image": "docker.io/liuhougangxa/tf-estimator-mnist",
                                    "command": [
                                        "python",
                                        "/opt/model.py",
                                        "--tf-train-steps=" + str(training_steps),
                                        "--tf-learning-rate=${trialParameters.learningRate}",
                                        "--tf-batch-size=${trialParameters.batchSize}"
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    # Configure parameters for the Trial template.
    trial_template = katib.V1beta1TrialTemplate(
        primary_container_name="tensorflow",
        primary_pod_labels={"training.kubeflow.org/job-role": "master"},
        trial_parameters=[
            katib.V1beta1TrialParameterSpec(
                name="learningRate",
                description="Learning rate for the training model",
                reference="learning_rate"
            ),
            katib.V1beta1TrialParameterSpec(
                name="batchSize",
                description="Batch size for the model",
                reference="batch_size"
            ),
        ],
        trial_spec=trial_spec
    )

    # Create an Experiment from the above parameters.
    experiment_spec = katib.V1beta1ExperimentSpec(
        max_trial_count=max_trial_count,
        max_failed_trial_count=max_failed_trial_count,
        parallel_trial_count=parallel_trial_count,
        objective=objective,
        algorithm=algorithm,
        parameters=parameters,
        trial_template=trial_template
    )

    # Create the KFP task for the Katib Experiment.
    # Experiment Spec should be serialized to a valid Kubernetes object.
    katib_experiment_launcher_op = components.load_component_from_url(
        "https://raw.githubusercontent.com/kubeflow/pipelines/master/components/kubeflow/katib-launcher/component.yaml")
    op = katib_experiment_launcher_op(
        experiment_name=experiment_name,
        experiment_namespace=experiment_namespace,
        experiment_spec=katib.ApiClient().sanitize_for_serialization(experiment_spec),
        experiment_timeout_minutes=60,
        delete_finished_experiment=False)

    return op
