### Notes on IAM for Kubeflow in AWS
For Terraform to spin up the necessary resources for AWS  I was able to find the following information regarding the required roles.

Per [this doc](https://awslabs.github.io/kubeflow-manifests/docs/deployment/prerequisites/#configure-aws-credentials-and-region-for-deployment). They want us to enable administrative privileges for the user that is running terraform. This is likely a hard sell for the CHI Eng team, but we can limit the privileges to the specific resources that we are creating. 

We can figure out the minimum resources needed by going to the terraform installation of kubeflow and running `TF_LOG=trace terraform apply --auto-approve &> log.log` then inspecting the log file created. 

So we will go through and see what resources we are creating and limit the privileges to those resources. The below resources are assuming that we are doing a kubeflow installation with rds and s3 and without cognito. The iam roles that I am listing below come from this json file [here](https://github.com/awslabs/kubeflow-manifests/blob/0d3af25d3ce226afbb0c677bf11e558320a7151d/tests/e2e/utils/rds-s3/auto-setup-iam-policy.json). 
- RDS: *
- S3: *
- EKS: * 
- Cloud formation: *
- Cloud control API: *
- IAM permissions: (can probably just do full access as well)
    + "iam:GetOpenIDConnectProvider"
    + "iam:CreateOpenIDConnectProvider"
    + "iam:TagOpenIDConnectProvider"
    + "iam:CreateRole"
    + "iam:AttachRolePolicy"
    + "iam:PutRolePolicy"
    + "iam:GetRole"
    + "iam:PassRole"
    + "iam:ListAttachedRolePolicies"
    + "iam:DetachRolePolicy"
- EC2: *
- Secrets Manager: Write

#### For kubeflow components that need access to AWS resources:
- kserve needs a service account in order to access the s3 bucket that will contain the model artifacts - doc [here](https://github.com/awslabs/kubeflow-manifests/blob/8e2ffc5958da6fd6e17790236c484938c20e318b/website/content/en/docs/component-guides/kserve/access-aws-services-from-kserve.md). So it needs a read only for s3 buckets, this can be limited to the specific bucket that we are using for our kserve models. It also needs access to the EC2ContainerRegistryReadOnly policy. 

- pipelines needs access to list s3 buckets and needs pod default manifest ran for the particular namespace. [doc](https://github.com/awslabs/kubeflow-manifests/blob/8e2ffc5958da6fd6e17790236c484938c20e318b/website/content/en/docs/component-guides/pipelines.md)


- profiles need access to a few different things - doc [here](https://github.com/awslabs/kubeflow-manifests/blob/4fb88f32e28bfce2e8395b2097f6360034e69a3d/website/content/en/docs/component-guides/profiles.md)
    + essentially will be linked to a service account. Will need access to s3 - read/write.
    +  Kubeflow admins will need to create an IAM role for each Profile with the desired scoped permissions.
    + The Profile controller does not have the permissions specified in the Profile roles.
    + The Profile controller has permissions to modify the Profile roles, which it will do to grant assume role permissions to the default-editor service account (SA) present in the Profile's namespace.
    + A default-editor SA exists in every Profile's namespace and will be annotated with the role ARN created for the profile. Pods annotated with the SA name will be granted the Profile role permissions.
    + The default-editor SA is used by various services in Kubeflow to launch resources in Profile namespaces. However, not all services do this by default.


- notebooks access needs - doc [here](https://github.com/awslabs/kubeflow-manifests/blob/4fb88f32e28bfce2e8395b2097f6360034e69a3d/website/content/en/docs/component-guides/notebooks.md)

- katib - doc [here](https://github.com/awslabs/kubeflow-manifests/blob/4fb88f32e28bfce2e8395b2097f6360034e69a3d/website/content/en/docs/component-guides/katib.md)