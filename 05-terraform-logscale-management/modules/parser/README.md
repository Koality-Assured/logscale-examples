# LogScale Parser Terraform Module

Manages LogScale parsers declaratively from external script files.

## Usage

```hcl
module "alb_parser" {
  source          = "../modules/parser"
  repository_name = "aws-alb-access-logs"
  parser_name     = "aws-alb-access"
  script_path     = "${path.module}/scripts/alb_parser.cql"
  tag_fields      = []
}
```
