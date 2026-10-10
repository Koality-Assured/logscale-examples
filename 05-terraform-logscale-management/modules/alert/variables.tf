variable "repository_name" {
  type        = string
  description = "Target repository where the alert executes"
}

variable "action_name" {
  type        = string
  description = "Name of the notification action"
}

variable "webhook_endpoint" {
  type        = string
  description = "Target HTTP webhook destination URL"
}

variable "body_template" {
  type        = string
  description = "JSON payload template sent to the webhook"
  default     = "{\"text\":\"LogScale Alert: {alert_name}\"}"
}

variable "alert_name" {
  type        = string
  description = "Descriptive name of the filter alert"
}

variable "alert_description" {
  type        = string
  description = "Detailed purpose and triage steps for the alert"
  default     = "Managed by Terraform"
}

variable "query_string" {
  type        = string
  description = "CQL query string evaluated on the event stream"
}

variable "enabled" {
  type        = bool
  description = "Whether the alert is actively evaluating events"
  default     = true
}
