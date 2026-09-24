resource "aws_cognito_user_pool" "relay_users" {
  name = "${local.name_prefix}-users"
  tags = { Project = "relay" }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }
}

resource "aws_cognito_user_pool_client" "web_client" {
  name                = "${local.name_prefix}-client"
  user_pool_id        = aws_cognito_user_pool.relay_users.id
  explicit_auth_flows = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  generate_secret     = false
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.web_client.id
}
