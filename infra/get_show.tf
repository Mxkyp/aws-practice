# Api: every GET route goes to the same Lambda; Powertools routes by path.
locals {
  get_show_routes = {
    show     = aws_api_gateway_resource.show.id     # /shows/{show_id}
    seasons  = aws_api_gateway_resource.seasons.id  # /shows/{show_id}/seasons
    season   = aws_api_gateway_resource.season.id   # …/seasons/{season}
    episodes = aws_api_gateway_resource.episodes.id # …/seasons/{season}/episodes
    episode  = aws_api_gateway_resource.episode.id  # …/episodes/{episode}
  }
}

resource "aws_api_gateway_method" "get_show" {
  for_each      = local.get_show_routes
  rest_api_id   = aws_api_gateway_rest_api.shows.id
  resource_id   = each.value
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_show" {
  for_each                = local.get_show_routes
  rest_api_id             = aws_api_gateway_rest_api.shows.id
  resource_id             = each.value
  http_method             = aws_api_gateway_method.get_show[each.key].http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.get_show.invoke_arn
}

# The single method/integration became the "show" entry of the maps above:
# rename them in state instead of destroying and recreating.
moved {
  from = aws_api_gateway_method.get_show
  to   = aws_api_gateway_method.get_show["show"]
}

moved {
  from = aws_api_gateway_integration.get_show
  to   = aws_api_gateway_integration.get_show["show"]
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
      Action   = ["dynamodb:GetItem", "dynamodb:Query"] # Query: list seasons/episodes
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
