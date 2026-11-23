resource "aws_dynamodb_table" "serie" {
  name = "serie"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "title"

  attribute {
    name = "title"
    type = "S"
  }

}
