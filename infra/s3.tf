resource "aws_s3_bucket" "some_bucket" {
  bucket = "aws-practice-lambda-code"
}

resource "aws_s3_object" "lambda_get_serie" {
  bucket = aws_s3_bucket.some_bucket.id

  key    = "get_serie.zip"
  source = data.archive_file.lambda_get_serie.output_path

  etag = filemd5(data.archive_file.lambda_get_serie.output_path)
}
