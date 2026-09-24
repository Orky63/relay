resource "aws_dynamodb_table" "tickets" {
  name         = "${local.name_prefix}-tickets"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project = var.project_name
    Env     = var.env
  }
}
