resource "aws_api_gateway_rest_api" "shows" {
    name = "shows-api"
}

resource "aws_api_gateway_resource" "shows" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_rest_api.shows.root_resource_id
  path_part   = "shows"
}

resource "aws_api_gateway_resource" "show" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_resource.shows.id
  path_part   = "{show_id}"
}

