terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    kestra = {
      source  = "kestra-io/kestra"
      version = "~> 0.7.0"
    }
  }
}

provider "aws" {
  region = var.default_region
}

provider "kestra" {
  # mandatory, the Kestra webserver/standalone URL
  url = "http://localhost:8080"
}

## vault
# provider "vault" {
#   address = var.vault_address
#   token   = var.vault_token
# }