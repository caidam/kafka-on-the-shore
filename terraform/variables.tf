# variables

# aws & s3
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

# api
variable "weather_api_key" {
  description = "Api key"
  type        = string
}

variable "cities_list" {
  description = "List of tracked cities"
  type        = string
}

# kafka
variable "kafka_host" {
  description = "Kafka host"
  type        = string
}

# docker
variable "docker_pat" {
  description = "docker pat"
  type        = string
}


# # vault #######
# variable "vault_address" {
#   description = "Address of the HCP Vault"
#   type        = string
# }

# variable "vault_token" {
#   description = "Token with relevant permissions to read, write, create, delete resources on the HCP Vault"
#   type        = string
# }