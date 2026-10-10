variable "repository_name" {
  type        = string
  description = "Target repository to associate the parser with"
}

variable "parser_name" {
  type        = string
  description = "Unique name of the parser"
}

variable "script_path" {
  type        = string
  description = "Relative or absolute path to the CQL/LQL parser script file"
}

variable "tag_fields" {
  type        = list(string)
  description = "Low-cardinality tag fields used for storage partitioning"
  default     = []
}
