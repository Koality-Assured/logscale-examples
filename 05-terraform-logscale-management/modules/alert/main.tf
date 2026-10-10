terraform {
  required_version = ">= 1.5.0"
  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }
}

resource "logscale_action" "webhook" {
  repository_name = var.repository_name
  name            = var.action_name
  type            = "webhook"
  endpoint        = var.webhook_endpoint
  body_template   = var.body_template
}

resource "logscale_filter_alert" "alert" {
  repository_name = var.repository_name
  name            = var.alert_name
  description     = var.alert_description
  query_string    = var.query_string
  enabled         = var.enabled
  action_ids      = [logscale_action.webhook.id]
}
