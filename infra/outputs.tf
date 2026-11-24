output "lambda_bucket_name" {
  description = "Name of the S3 bucket used to store function code."

  value = aws_s3_bucket.some_bucket.id
}

output "get_serie_function_name" {
  value = aws_lambda_function.get_serie.function_name
}
