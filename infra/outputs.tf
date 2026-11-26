output "lambda_bucket_name" {
  description = "Name of the S3 bucket used to store function code."

  value = aws_s3_bucket.some_bucket.id
}

output "get_show_function_name" {
  value = aws_lambda_function.get_show.function_name
}

output "api_invoke_url" {
  description = "Stage URL on aws-emulator (api id + stage in the path; *.execute-api hosts don't resolve locally)"
  value       = "https://127.0.0.1:9297/_aws/execute-api/${aws_api_gateway_rest_api.shows.id}/${aws_api_gateway_deployment.shows.stage_name}"
}

