resource "aws_sns_topic" "notifications" {
  name = "${local.name_prefix}-notifications"
}
