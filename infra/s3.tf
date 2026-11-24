resource "aws_s3_bucket" "some_bucket" {
  bucket = "aws-practice-lambda-code"
}

resource "aws_s3_object" "placeholder" {
  bucket = aws_s3_bucket.some_bucket.id

  key    = "placeholder.zip"
  source = data.archive_file.placeholder.output_path

  etag = data.archive_file.placeholder.output_md5
}
