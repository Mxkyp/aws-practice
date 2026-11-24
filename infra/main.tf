terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source = "hashicorp/archive"
      version = "~> 2.8.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "archive_file" "lambda_get_serie" {
  type = "zip"

  source_dir  = "${path.module}/../functions/get_serie"
  output_path = "${path.module}/../functions/get_serie.zip"
}

