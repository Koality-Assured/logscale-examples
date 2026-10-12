terraform {
  required_version = ">= 1.5.0"
  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }
}

resource "logscale_repository" "repo" {
  name           = var.repository_name
  description    = var.description
  retention_days = var.retention_days
}

resource "logscale_view" "view" {
  count       = var.create_federated_view ? 1 : 0
  name        = "${var.repository_name}-view"
  description = "Federated query view for ${var.repository_name}"

  dynamic "repository_connection" {
    for_each = concat([logscale_repository.repo.name], var.additional_view_repositories)
    content {
      repository_name = repository_connection.value
      filter          = "*"
    }
  }
}
