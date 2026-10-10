variable "repository_name" {
  type        = string
  description = "Unique name for the LogScale repository"
}

variable "description" {
  type        = string
  description = "Human-readable description of repository contents"
  default     = "Managed by Terraform"
}

variable "retention_days" {
  type        = number
  description = "Number of days before log events are purged"
  default     = 90
}

variable "storage_size_limit_gb" {
  type        = number
  description = "Maximum storage allocation in gigabytes (0 for unlimited)"
  default     = 0
}

variable "create_federated_view" {
  type        = bool
  description = "Whether to create a companion federated view"
  default     = true
}

variable "additional_view_repositories" {
  type        = list(string)
  description = "Additional repositories to include in the federated view"
  default     = []
}
