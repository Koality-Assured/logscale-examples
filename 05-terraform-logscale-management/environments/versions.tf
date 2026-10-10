terraform {
  required_version = ">= 1.5.0"

  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }

  # Example remote S3 state backend configuration with native lockfile locking
  # backend "s3" {
  #   bucket       = "example-corp-logscale-tf-state"
  #   key          = "logscale-saas/terraform.tfstate"
  #   region       = "us-east-1"
  #   use_lockfile = true
  # }
}

provider "logscale" {
  api_url   = var.logscale_api_url
  api_token = var.logscale_api_token
}
