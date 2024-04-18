# variables
variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "user_name" {
  description = "The name of the IAM user"
  type        = string
}

variable "default_region" {
  description = "The name of the IAM user default region"
  type        = string
}

variable "weather_api_key" {
  description = "Api key"
  type        = string
}

variable "cities_list" {
  description = "List of tracked cities"
  type        = string
}

variable "kafka_host" {
  description = "Kafka host"
  type        = string
}

# data "aws_iam_user" "s3_user" {
#   user_name = var.user_name
# }

# s3 bucket
resource "aws_s3_bucket" "kafka-bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "kafka-bucket"
    Environment = "Dev"
  }
  }

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.kafka-bucket.id

  policy = <<-POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "${aws_iam_user.s3_user.arn}"},
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::${var.bucket_name}",
        "arn:aws:s3:::${var.bucket_name}/*"
      ]
    }
  ]
}
POLICY
}

# s3 policy
# "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"],
# "Action": ["s3:*"],
resource "aws_iam_policy" "s3_policy" {
  # name        = "MyS3Policy"
  # description = "My test S3 policy"
  name        = "kafka-ots-s3-policy"
  description = "S3 policy for kafka project"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::${var.bucket_name}/*"]
    }
  ]
}
EOF
}

# dedicated iam user
resource "aws_iam_user" "s3_user" {
  name = var.user_name
  path = "/system/"
}

resource "aws_iam_access_key" "s3_user_keys" {
  user = aws_iam_user.s3_user.name
}

resource "aws_iam_user_policy_attachment" "s3_user_policy_attachment" {
  user       = aws_iam_user.s3_user.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

# save credentials
resource "null_resource" "credentials_file" {
  provisioner "local-exec" {
    command = <<-EOF
      echo AWS_ACCESS_KEY=${aws_iam_access_key.s3_user_keys.id} > ../.env &&
      echo AWS_SECRET_KEY=${aws_iam_access_key.s3_user_keys.secret} >> ../.env &&
      echo S3_BUCKET_NAME=${var.bucket_name} >> ../.env &&
      echo AWS_DEFAUL_REGION=${var.default_region} >> ../.env &&
      echo KAFKA_HOST=${var.kafka_host} >> ../.env &&
      echo WEATHER_API_KEY=${var.weather_api_key} >> ../.env &&
      echo CITIES=${var.cities_list} >> ../.env &&
      make -C ../consolidation/ all

    EOF
  }
  depends_on = [aws_iam_access_key.s3_user_keys]
}

# variables
variable "docker_pat" {
  description = "docker pat"
  type        = string
}

# update kestra flow
resource "kestra_flow" "example" {
  namespace = "kafka-ots"
  flow_id   = "kafka-ots-consolidation"
  content   = <<EOT
# Kestra flow
# id: "kafka-ots-consolidation"
# namespace: "kafka-ots"

tasks:
  - id: python
    type: io.kestra.plugin.scripts.python.Commands
#    namespaceFiles: 
#      enabled: true
    runner: DOCKER
    docker:
      image: caidam/private:kots-consolidation
      config: |
        {
          "auths": {
              "https://index.docker.io/v1/": {
                  "username": "caidam",
                  "password": "${ var.docker_pat }"
              }
          }
        }
    commands:
      - python /app/consolidate_files.py

triggers:
  # Here we use the 'Schedule' trigger to run the flow every hour on the dot.
- id: every1Hour
  type: io.kestra.core.models.triggers.types.Schedule
  cron: "0 * * * *"
EOT
}