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

resource "aws_api_gateway_resource" "seasons" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_resource.show.id
  path_part   = "seasons"
}

resource "aws_api_gateway_resource" "season" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_resource.seasons.id
  path_part   = "{season}"
}

resource "aws_api_gateway_resource" "episodes" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_resource.season.id
  path_part   = "episodes"
}

resource "aws_api_gateway_resource" "episode" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  parent_id   = aws_api_gateway_resource.episodes.id
  path_part   = "{episode}"
}

resource "aws_api_gateway_deployment" "shows" {
  rest_api_id = aws_api_gateway_rest_api.shows.id
  stage_name  = "dev" # WORKAROUND: emulator rejects stageName "" (see notes); AWS-idiomatic = separate aws_api_gateway_stage

  triggers = {
    # Every resource/method/integration the stage serves; a change to any of
    # them must produce a new deployment snapshot.
    redeploy = sha1(jsonencode([
      aws_api_gateway_resource.show,
      aws_api_gateway_resource.seasons,
      aws_api_gateway_resource.season,
      aws_api_gateway_resource.episodes,
      aws_api_gateway_resource.episode,
      aws_api_gateway_method.get_show,
      aws_api_gateway_integration.get_show,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# resource "aws_api_gateway_stage" "dev" {
#   rest_api_id   = aws_api_gateway_rest_api.shows.id
#   deployment_id = aws_api_gateway_deployment.shows.id
#   stage_name    = "dev"
# }


