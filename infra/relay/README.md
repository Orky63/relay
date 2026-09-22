# Relay — Serverless Incident Portal (Terraform)

This folder contains a Terraform scaffold to deploy Relay core infra: API Gateway (HTTP API), Lambda, DynamoDB, Cognito, S3, SNS, EventBridge and CloudWatch.

Prerequisites:

- AWS CLI configured with credentials
- Terraform 1.0+
- Zip installed (used to package the local Lambda)

Quick deploy:

```
cd infra/relay
terraform init
terraform apply -var="region=us-east-1"
```

Notes:

- SES domain verification and advanced SES settings are environment-specific and not included here.
- The Terraform packages the local Lambda from `services/relay_lambda/handler.py` into `infra/relay/build/relay.zip` using a local-exec zip command.
- Set the environment variable `TICKETS_TABLE` for the Lambda via Terraform if desired (simple extension).
 
CI / Deploy:

- A GitHub Actions CI workflow is included at `.github/workflows/ci.yml` which runs `terraform fmt`/`init`/`validate` and Python `pytest` for the Lambda tests.
- A deploy workflow is included at `.github/workflows/deploy.yml` that runs `terraform apply` on pushes to `master`/`main`. Create the following GitHub secrets in the repo settings:
	- `AWS_ACCESS_KEY_ID`
	- `AWS_SECRET_ACCESS_KEY`
	- `AWS_REGION`

