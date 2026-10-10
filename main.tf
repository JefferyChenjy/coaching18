terraform {
  backend "s3" {
    bucket       = "sctp-tfstate-ce13"
    key          = "group1coaching18/terraform.tfstate"
    region       = "us-east-1"
  }
}

provider "aws" {
   region = "us-east-1"
}