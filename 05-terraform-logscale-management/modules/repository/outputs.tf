output "repository_name" {
  description = "Name of the created repository"
  value       = logscale_repository.repo.name
}

output "view_name" {
  description = "Name of the federated view (if created)"
  value       = var.create_federated_view ? logscale_view.view[0].name : null
}
