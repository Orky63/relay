# Relay — Serverless Incident Portal (Terraform)

This folder contains a Terraform scaffold to deploy Relay core infra: API Gateway (HTTP API), Lambda, DynamoDB, Cognito, S3, SNS, EventBridge and CloudWatch.

Prerequisites:

- AWS CLI configured with credentials
- Terraform 1.10+ (CI uses 1.15.8)

Quick deploy:

```
cd infra/relay
terraform init
terraform apply -var="region=us-east-1"
```

Notes:

- SES domain verification and advanced SES settings are environment-specific and not included here.
- Terraform packages the local Lambda from `services/relay_lambda/handler.py` into `infra/relay/build/relay.zip` using the archive provider.
- Set the environment variable `TICKETS_TABLE` for the Lambda via Terraform if desired (simple extension).
 
CI / Deploy:

- The state backend bucket `relay-terraform-state-387344700059` was bootstrapped
  separately in `us-east-1`, with versioning, AES256 encryption, and all four S3
  public-access blocks enabled. It must exist before `terraform init`.
  `terraform-state-policy.json` records the `relay-terraform-state` inline policy
  applied to `github-relay`: bucket listing, state reads/writes, and lock
  reads/writes/deletion. State deletion is not granted.
- `provider-compatibility-policy.json` records the additional
  `relay-provider-compatibility` inline policy on `github-relay`, added after
  deployment identified missing provider permissions. Its stage-tagging grant
  targets the deployed API ID; review it if the API is replaced.
  On 2026-09-24, API Gateway explicitly denied `apigateway:TagResource` during
  stage creation, and deployment succeeded after this scoped grant was added.
  Access Analyzer nevertheless reported that action as `INVALID_ACTION`;
  recheck this service/validator discrepancy when revising the policy.
- To restore these inline policies as an administrator, run from this directory:
  `aws iam put-user-policy --user-name github-relay --policy-name relay-terraform-state --policy-document file://terraform-state-policy.json`
  and
  `aws iam put-user-policy --user-name github-relay --policy-name relay-provider-compatibility --policy-document file://provider-compatibility-policy.json`.

- Before the first deployment, upload `setup-deploy-permissions.py` to AWS CloudShell
  while signed in as `Andy_admin` in account `387344700059`. Run
  `python3 setup-deploy-permissions.py` to preview the policies, then
  `python3 setup-deploy-permissions.py --apply` to validate them with AWS IAM Access
  Analyzer, create them, and attach `relay-github-deploy` to the existing
  `github-relay` user. This does not create access keys or deploy infrastructure.
- These permissions target the default `relay-dev` resources in `us-east-1`.
  Cognito and API Gateway access requires `Project=relay` tags. The Lambda role
  must use the administrator-created `relay-lambda-boundary` policy. Keep these
  Terraform changes with the permission setup. Changing region, environment, or
  project name requires reviewing the policies as well.
- The bootstrap script refuses to overwrite a different existing policy. A live
  deployment succeeded on 2026-09-24 with the additional inline policies above.
  Review any new denied operation against the specific resource before
  expanding access.

- A GitHub Actions CI workflow is included at `.github/workflows/ci.yml` which runs `terraform fmt`/`init`/`validate` and Python `pytest` for the Lambda tests.
- A deploy workflow is included at `.github/workflows/deploy.yml` that runs `terraform apply` on pushes to `master`/`main`. Create the following GitHub secrets in the repo settings:
	- `AWS_ACCESS_KEY_ID`
	- `AWS_SECRET_ACCESS_KEY`
	- `AWS_REGION`
