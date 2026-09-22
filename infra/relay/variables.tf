variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "relay"
}

variable "env" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
