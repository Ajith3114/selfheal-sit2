terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.62.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region = "ap-south-1"
#  profile = var.aws_profile
}

terraform {
  backend "s3" {
    bucket = "accesser-user1-bucket1-2026"
    key    = "2026/dev/terraform.tfstate"
    region = "eu-north-1"
  }
}
