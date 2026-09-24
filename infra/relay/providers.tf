terraform {
  required_version = ">= 1.10, < 2.0"
  backend "s3" {
    bucket       = "relay-terraform-state-387344700059"
    key          = "relay/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}
