output "s3_bucket_name" {
  value = aws_s3_bucket.brew_mirror_bucket.bucket
}

output "lambda_function_arn" {
  value = aws_lambda_function.brew_mirror_function.arn
}