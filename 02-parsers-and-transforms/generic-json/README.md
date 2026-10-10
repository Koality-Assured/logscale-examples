# Generic JSON Parser

High-performance baseline JSON parser for application and container logs.

## Parser Design Notes

- **Dynamic Flattening**: Calls `parseJson()` to automatically extract all top-level keys into event fields without explicit regex expressions.
- **Bounded Tag Cardinality**: Only tags low-cardinality metadata (`#level` and `#service`). High-cardinality attributes (`transaction_id`, `user_id`) remain untagged regular fields.
