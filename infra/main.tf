terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.8.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "archive_file" "placeholder" {
  type        = "zip"
  output_path = "${path.module}/../build/placeholder.zip"

  source {
    filename = "handler.py"
    content  = <<-EOT
      def lambda_handler(event, context):
          return "not deployed yet"
    EOT
  }
}
