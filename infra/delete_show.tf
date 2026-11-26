# Api: DELETE routes go to their own Lambda, so only this role can write.
resource "aws_api_gateway_method" "delete_episode" {
  rest_api_id   = aws_api_gateway_rest_api.shows.id
  resource_id   = aws_api_gateway_resource.episode.id # …/episodes/{episode}
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "delete_episode" {
  rest_api_id             = aws_api_gateway_rest_api.shows.id
  resource_id             = aws_api_gateway_resource.episode.id
  http_method             = aws_api_gateway_method.delete_episode.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST" # Lambda is always invoked with POST, whatever the route's method
  uri                     = aws_lambda_function.delete_show.invoke_arn
}

resource "aws_lambda_permission" "delete_show_api" {
  statement_id  = "allow-api-gateway-delete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_show.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.shows.execution_arn}/*/DELETE/shows/*"
}

# Policies
resource "aws_iam_role" "delete_show" {
  name = "delete-show"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "delete_show_logs" {
  role       = aws_iam_role.delete_show.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "delete_show_write" {
  name = "delete-shows"
  role = aws_iam_role.delete_show.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:DeleteItem"]
      Resource = aws_dynamodb_table.shows.arn
    }]
  })
}

resource "aws_lambda_function" "delete_show" {
  function_name = "delete_show"
  role          = aws_iam_role.delete_show.arn
  runtime       = "python3.12"
  handler       = "handler.lambda_handler"

  environment {
    variables = { TABLE_NAME = aws_dynamodb_table.shows.name }
  }

  s3_bucket = aws_s3_bucket.some_bucket.id
  s3_key    = aws_s3_object.placeholder.key

  lifecycle {
    ignore_changes = [s3_bucket, s3_key, s3_object_version, source_code_hash]
  }
}
