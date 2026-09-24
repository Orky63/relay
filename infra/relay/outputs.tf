output "api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}

output "dynamodb_table" {
  value = aws_dynamodb_table.tickets.name
}

output "s3_bucket" {
  value = aws_s3_bucket.attachments.bucket
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.relay_users.id
}

output "lambda_arn" {
  value = aws_lambda_function.api_handler.arn
}
