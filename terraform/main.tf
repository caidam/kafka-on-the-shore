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

# Generate Makefile for consolidation image push
data "template_file" "makefile" {
  template = file("${path.module}/templates/Makefile.tpl")

  vars = {
    DOCKERHUB_USERNAME = var.dockerhub_username
    IMAGE_NAME         = var.docker_image_name
    IMAGE_TAG          = var.docker_image_tag
  }
}

# Write the generated Makefile to a file in the parent directory
resource "local_file" "makefile" {
  content  = data.template_file.makefile.rendered
  filename = "${path.module}/../consolidation/Makefile"
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
      image: ${var.dockerhub_username}/${var.docker_image_name}:${var.docker_image_tag}
      config: |
        {
          "auths": {
              "https://index.docker.io/v1/": {
                  "username": "${var.dockerhub_username}",
                  "password": "${var.docker_pat}"
              }
          }
        }
    commands:
      - python /app/consolidate_files.py

triggers:
  # Here we use the 'Schedule' trigger to run the flow every 15 minutes on the dot.
- id: every15Mn
  type: io.kestra.core.models.triggers.types.Schedule
  cron: "*/15 * * * *"
EOT
}



# # VAULT - UNCOMMENT BELOW (+ related variables and provider) TO WRITE SECRETS TO A VAULT INSTANCE #########
# module "vault_secrets" {
#   source = "git::https://github.com/caidam/terraform_modules.git//vault_secrets"

#   mount_path = "kafka_project" # Name of the kv store

#   token_ttl = "768h" # The Time To Live period of the token, specified as a numeric string with suffix like '30s' or '5m'

#   # edit the data_json.tpl file and add the variables accordingly, you can create additional variables and use .tfvars to avoid hardcoding sensitive information
#   data_json = templatefile("${path.module}/templates/data_json.tpl", {
#     aws_access_key     = aws_iam_access_key.s3_user_keys.id
#     aws_secret_key     = aws_iam_access_key.s3_user_keys.secret,
#     s3_bucket_name     = var.bucket_name,
#     aws_default_region = var.default_region,
#     kafka_host         = var.kafka_host,
#     weather_api_key    = var.weather_api_key,
#     cities_list        = var.cities_list
#   })

#   depends_on = [null_resource.credentials_file]
# }
