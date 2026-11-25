# Api
resource "aws_api_gateway_method" "get_show" {
  rest_api_id   = aws_api_gateway_rest_api.shows.id
  resource_id   = aws_api_gateway_resource.show.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_show" {
  rest_api_id             = aws_api_gateway_rest_api.shows.id
  resource_id             = aws_api_gateway_resource.show.id
  http_method             = aws_api_gateway_method.get_show.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.get_show.invoke_arn
}

resource "aws_lambda_permission" "get_show_api" {
  statement_id  = "allow-api-gateway-get"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_show.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.shows.execution_arn}/*/GET/shows/*"
}

# Policies
resource "aws_iam_role" "get_show" {
  name = "get-show"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "get_show_logs" {
  role       = aws_iam_role.get_show.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "get_show_read" {
  name = "read-shows"
  role = aws_iam_role.get_show.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "dynamodb:GetItem"
      Resource = aws_dynamodb_table.shows.arn
    }]
  })
}

resource "aws_lambda_function" "get_show" {
  function_name = "get_show"
  role          = aws_iam_role.get_show.arn
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
