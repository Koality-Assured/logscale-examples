terraform {
  required_version = ">= 1.5.0"
  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }
}

resource "logscale_webhook_action" "webhook" {
  view_name     = var.repository_name
  name          = var.action_name
  method        = "POST"
  url           = var.webhook_endpoint
  body_template = var.body_template
  use_proxy     = false
  ignore_ssl    = false
}

resource "logscale_filter_alert" "alert" {
  view_name            = var.repository_name
  name                 = var.alert_name
  description          = var.alert_description
  query_string         = var.query_string
  enabled              = var.enabled
  query_ownership_type = "Organization"
  action_ids_or_names  = [logscale_webhook_action.webhook.name]
}
