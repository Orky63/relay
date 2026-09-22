locals {
  name_prefix = "${var.project_name}-${var.env}"
}

resource "aws_s3_bucket" "attachments" {
  bucket = "${local.name_prefix}-attachments"
  acl    = "private"
}
