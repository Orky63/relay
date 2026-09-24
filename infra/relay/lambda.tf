data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../../services/relay_lambda/handler.py"
  output_path = "${path.module}/build/relay.zip"
}

resource "aws_lambda_function" "api_handler" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${local.name_prefix}-api-handler"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  source_code_hash = data.archive_file.lambda.output_base64sha256

  environment {
    variables = {
      TICKETS_TABLE = aws_dynamodb_table.tickets.name
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_basic_exec, aws_iam_role_policy.lambda_dynamodb]
}
