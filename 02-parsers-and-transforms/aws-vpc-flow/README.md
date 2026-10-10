# AWS VPC Flow Log Parser

High-speed positional parser for Amazon VPC Flow Logs (default version 2 space-delimited syntax).

## Parser Design Notes

- **CSV Positional Parsing**: Uses `parseCsv(separator: " ")` to parse positional fields directly without expensive regex backtracking.
- **Numeric Casting**: Converts `packets`, `bytes`, `srcport`, and `dstport` to numeric values via `parseNumber()` at ingest time so mathematical aggregations (`sum(bytes)`, `avg(packets)`) run at native hardware speeds.
- **Low-Cardinality Tagging**: Tags `#action` (`ACCEPT` vs `REJECT`). Because `#action` has only two possible values, it creates exactly two index segments per block, allowing security queries targeting rejected traffic (`#action = REJECT`) to skip accepted traffic blocks entirely!
