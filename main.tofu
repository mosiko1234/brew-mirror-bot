provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "brew_mirror_bucket" {
  bucket = "brew-mirror-bucket"

  versioning {
    enabled = true
  }

  tags = {
    Name        = "Brew Mirror Bucket"
    Environment = "dev"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-brew-mirror-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name   = "lambda-brew-mirror-policy"
  role   = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Effect   = "Allow"
      Resource = [
        "${aws_s3_bucket.brew_mirror_bucket.arn}",
        "${aws_s3_bucket.brew_mirror_bucket.arn}/*"
      ]
    }]
  })
}

resource "aws_lambda_function" "brew_mirror_function" {
  function_name = "brew-mirror-lambda"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"

  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.brew_mirror_bucket.bucket
    }
  }
}
