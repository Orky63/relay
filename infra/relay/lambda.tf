resource "null_resource" "package_lambda" {
  triggers = {
    source_md5 = filesha256("${path.root}/services/relay_lambda/handler.py")
  }

  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/build && /usr/bin/zip -j ${path.module}/build/relay.zip ${path.root}/services/relay_lambda/handler.py"
  }
}

resource "aws_lambda_function" "api_handler" {
  filename         = "${path.module}/build/relay.zip"
  function_name    = "${local.name_prefix}-api-handler"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/build/relay.zip")

  environment {
    variables = {
      TICKETS_TABLE = aws_dynamodb_table.tickets.name
    }
  }

  depends_on = [null_resource.package_lambda]
}
