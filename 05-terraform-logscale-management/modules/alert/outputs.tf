output "alert_id" {
  description = "Identifier of the created filter alert"
  value       = logscale_filter_alert.alert.id
}

output "action_id" {
  description = "Identifier of the created webhook action"
  value       = logscale_action.webhook.id
}
