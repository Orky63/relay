resource "aws_cloudwatch_event_rule" "incidents" {
  name = "${local.name_prefix}-incidents"
  event_pattern = jsonencode({
    source = ["relay"]
  })
}

resource "aws_cloudwatch_event_target" "incidents_target" {
  rule = aws_cloudwatch_event_rule.incidents.name
  arn  = aws_lambda_function.api_handler.arn
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.incidents.arn
}
