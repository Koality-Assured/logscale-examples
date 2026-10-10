output "unified_view_name" {
  description = "Name of the global cross-repository query view"
  value       = logscale_view.unified_view.name
}

output "vpc_flow_feed_id" {
  description = "ID of the S3-SQS ingest feed"
  value       = module.feed_vpc_flow.feed_id
}

output "root_login_alert_id" {
  description = "ID of the root account login filter alert"
  value       = module.alert_root_login.alert_id
}
