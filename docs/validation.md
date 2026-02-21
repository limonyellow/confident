# Validation

In order to avoid misconfigurations, Confident will supply indicative errors in case of wrong values or wrong sequence of arguments.
For instance:

- Wrong or missing files provided.
- Inserting both `map_name` and `map_field` (causing ambiguous config map selection).
- Wrong types or missing values (by pydantic's [validation mechanism](https://docs.pydantic.dev/latest/concepts/validators/)).
