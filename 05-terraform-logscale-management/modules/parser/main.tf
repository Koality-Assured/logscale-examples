terraform {
  required_version = ">= 1.5.0"
  required_providers {
    logscale = {
      source  = "koality-assured/logscale"
      version = "~> 0.1.0"
    }
  }
}

resource "logscale_parser" "parser" {
  repository_name = var.repository_name
  name            = var.parser_name
  script          = file(var.script_path)
  fields_to_tag   = var.tag_fields
}
