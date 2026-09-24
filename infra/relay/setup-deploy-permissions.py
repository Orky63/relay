#!/usr/bin/env python3
"""Run in AWS CloudShell as Andy_admin. Creates no users, keys, or app resources.

Preview: python3 setup-deploy-permissions.py
Apply:   python3 setup-deploy-permissions.py --apply

Creates two managed policies and attaches only the deployment policy to
github-relay. Existing policies must match exactly; this script never overwrites
an existing policy. Requires the accompanying Terraform boundary and tag changes.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote

ACCOUNT = "387344700059"
REGION = "us-east-1"
PREFIX = "relay-dev"
BOUNDARY = f"arn:aws:iam::{ACCOUNT}:policy/relay-lambda-boundary"
ROLE = f"arn:aws:iam::{ACCOUNT}:role/{PREFIX}-lambda-role"


def allow(actions, resources, condition=None):
    statement = {"Effect": "Allow", "Action": actions, "Resource": resources}
    if condition:
        statement["Condition"] = condition
    return statement


def document(statements):
    return {"Version": "2012-10-17", "Statement": statements}


tagged = {"StringEquals": {"aws:ResourceTag/Project": "relay"}}
creation_tags = {"StringEquals": {"aws:RequestTag/Project": "relay"}}
table = f"arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{PREFIX}-tickets"
bucket = f"arn:aws:s3:::{PREFIX}-attachments"
logs = f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:/aws/lambda/{PREFIX}-api-handler"
api = f"arn:aws:apigateway:{REGION}::"
pool = f"arn:aws:cognito-idp:{REGION}:{ACCOUNT}:userpool/*"

boundary = document([
    allow(["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], [logs, logs + ":*"]),
    allow(["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query", "dynamodb:UpdateItem"], table),
    allow(["s3:GetObject", "s3:PutObject"], bucket + "/*"),
])

deployment = document([
    allow(["iam:CreateRole", "iam:PutRolePermissionsBoundary"], ROLE,
          {"StringEquals": {"iam:PermissionsBoundary": BOUNDARY}}),
    allow(["iam:GetRole", "iam:DeleteRole", "iam:UpdateAssumeRolePolicy",
           "iam:UpdateRole", "iam:TagRole", "iam:UntagRole", "iam:ListRoleTags",
           "iam:GetRolePolicy", "iam:PutRolePolicy", "iam:DeleteRolePolicy",
           "iam:ListRolePolicies", "iam:ListAttachedRolePolicies"], ROLE),
    allow(["iam:AttachRolePolicy", "iam:DetachRolePolicy"], ROLE,
          {"ArnEquals": {"iam:PolicyARN": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"}}),
    allow("iam:PassRole", ROLE, {"StringEquals": {"iam:PassedToService": "lambda.amazonaws.com"}}),
    allow(["lambda:CreateFunction", "lambda:GetFunction", "lambda:GetFunctionConfiguration",
           "lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction",
           "lambda:GetPolicy", "lambda:AddPermission", "lambda:RemovePermission",
           "lambda:ListVersionsByFunction", "lambda:ListTags", "lambda:TagResource", "lambda:UntagResource",
           "lambda:GetFunctionCodeSigningConfig", "lambda:GetRuntimeManagementConfig",
           "lambda:GetFunctionConcurrency", "lambda:PutFunctionConcurrency", "lambda:DeleteFunctionConcurrency"],
          f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{PREFIX}-api-handler"),
    allow(["dynamodb:CreateTable", "dynamodb:UpdateTable", "dynamodb:DeleteTable",
           "dynamodb:DescribeTable", "dynamodb:DescribeContinuousBackups", "dynamodb:DescribeTimeToLive",
           "dynamodb:UpdateContinuousBackups", "dynamodb:UpdateTimeToLive",
           "dynamodb:ListTagsOfResource", "dynamodb:TagResource", "dynamodb:UntagResource"], table),
    allow(["s3:CreateBucket", "s3:DeleteBucket", "s3:ListBucket", "s3:GetBucket*",
           "s3:GetEncryptionConfiguration", "s3:GetLifecycleConfiguration", "s3:GetReplicationConfiguration",
           "s3:PutBucketAcl", "s3:PutBucketTagging"], bucket),
    allow(["logs:CreateLogGroup", "logs:DeleteLogGroup", "logs:PutRetentionPolicy",
           "logs:DeleteRetentionPolicy", "logs:ListTagsForResource", "logs:ListTagsLogGroup",
           "logs:TagResource", "logs:UntagResource", "logs:TagLogGroup", "logs:UntagLogGroup"], [logs, logs + ":*"]),
    allow("logs:DescribeLogGroups", "*", {"StringEquals": {"aws:RequestedRegion": REGION}}),
    allow(["events:PutRule", "events:DeleteRule", "events:DescribeRule", "events:PutTargets",
           "events:RemoveTargets", "events:ListTargetsByRule", "events:ListTagsForResource",
           "events:TagResource", "events:UntagResource"], f"arn:aws:events:{REGION}:{ACCOUNT}:rule/{PREFIX}-incidents"),
    allow(["sns:CreateTopic", "sns:DeleteTopic", "sns:GetTopicAttributes", "sns:SetTopicAttributes",
           "sns:ListTagsForResource", "sns:TagResource", "sns:UntagResource"],
          f"arn:aws:sns:{REGION}:{ACCOUNT}:{PREFIX}-notifications"),
    allow("cognito-idp:CreateUserPool", "*",
          {"StringEquals": {"aws:RequestTag/Project": "relay", "aws:RequestedRegion": REGION}}),
    allow(["cognito-idp:DescribeUserPool", "cognito-idp:UpdateUserPool", "cognito-idp:DeleteUserPool",
           "cognito-idp:CreateUserPoolClient", "cognito-idp:DescribeUserPoolClient",
           "cognito-idp:UpdateUserPoolClient", "cognito-idp:DeleteUserPoolClient",
           "cognito-idp:ListTagsForResource", "cognito-idp:TagResource", "cognito-idp:UntagResource"], pool, tagged),
    allow("apigateway:POST", api + "/apis", creation_tags),
    allow(["apigateway:GET", "apigateway:POST", "apigateway:PUT", "apigateway:PATCH", "apigateway:DELETE"],
          [api + "/apis/*", api + "/tags/*"], tagged),
])


def aws(*args):
    result = subprocess.run(["aws", *args, "--output", "json", "--no-cli-pager"],
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    policies = {"relay-lambda-boundary": boundary, "relay-github-deploy": deployment}
    for name, policy in policies.items():
        if len(json.dumps(policy, separators=(",", ":"))) > 6144:
            raise RuntimeError(f"Policy exceeds the managed-policy size limit: {name}")
    if not args.apply:
        print(json.dumps(policies, indent=2))
        print("Preview only. Run with --apply to create and attach the policies.")
        return
    identity = aws("sts", "get-caller-identity")
    if identity["Account"] != ACCOUNT or identity["Arn"] != f"arn:aws:iam::{ACCOUNT}:user/Andy_admin":
        raise RuntimeError("Run this in CloudShell signed in as Andy_admin in the Relay account.")
    aws("iam", "get-user", "--user-name", "github-relay")
    for name, policy in policies.items():
        validation = aws("accessanalyzer", "validate-policy", "--region", REGION,
                         "--policy-type", "IDENTITY_POLICY", "--policy-document", json.dumps(policy))
        errors = [finding for finding in validation["findings"] if finding["findingType"] == "ERROR"]
        if errors:
            raise RuntimeError(f"AWS rejected {name}: {json.dumps(errors)}")
    # Check both policies before making changes, so an existing name is never overwritten.
    missing = []
    for name, policy in policies.items():
        arn = f"arn:aws:iam::{ACCOUNT}:policy/{name}"
        try:
            existing = aws("iam", "get-policy", "--policy-arn", arn)["Policy"]
        except RuntimeError as error:
            if "NoSuchEntity" not in str(error):
                raise
            missing.append(name)
            continue
        saved = aws("iam", "get-policy-version", "--policy-arn", arn,
                    "--version-id", existing["DefaultVersionId"])["PolicyVersion"]["Document"]
        if isinstance(saved, str):
            saved = json.loads(unquote(saved))
        if saved != policy:
            raise RuntimeError(f"Existing {name} differs; stopped without overwriting it.")
    with tempfile.TemporaryDirectory(prefix="relay-iam-") as directory:
        for name in missing:
            path = Path(directory) / (name + ".json")
            path.write_text(json.dumps(policies[name]))
            aws("iam", "create-policy", "--policy-name", name,
                "--policy-document", "file://" + str(path), "--tags", "Key=Project,Value=relay")
            print(f"Created {name}")
    arn = f"arn:aws:iam::{ACCOUNT}:policy/relay-github-deploy"
    aws("iam", "attach-user-policy", "--user-name", "github-relay", "--policy-arn", arn)
    attached = aws("iam", "list-attached-user-policies", "--user-name", "github-relay")
    if not any(p["PolicyArn"] == arn for p in attached["AttachedPolicies"]):
        raise RuntimeError("Attachment not yet visible; rerun this script to verify.")
    print("Verified: relay-github-deploy attached to github-relay. No access keys created.")


if __name__ == "__main__":
    main()
