.. _validation:

Validation
==========

In order to avoid misconfigurations, `Confident` will supply indicative errors in case of wrong values or wrong sequence of arguments.
For instance:

- Wrong or missing files provided.
- Inserting both `deployment_name` and `deployment_field` (causing ambiguous deployment selection).
- Wrong types or missing values (by `pydantic` validation mechanism).
