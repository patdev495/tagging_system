Status: completed

# Erro 04 catalog and Product seed

## What to build

Make `erro_04` Products manageable end-to-end in the catalog and initialize the production catalog from the complete rows of PD027032 Table 1. An Admin must configure and validate the label-specific Product metadata, including the Erro 04 Carton ID Prefix, Factory Item Code, required Revision, and existing print metadata; the packing station must then use the configuration without hard-coded SKU rules.

Seed the 16 complete table rows with their UPC, SKU, Supplier PN, packed quantity, SKU Description, Factory Item Code, Carton ID Prefix, Revision, and initial scale configuration. Do not seed `NYS6248` because the supplied table lacks its UPC and SKU.

## Acceptance criteria

- [x] The Product API and Admin catalog can create, edit, display, and validate `erro_04` Products with required `carton_id_prefix` (`H` or `K`), `factory_item_code`, and Revision.
- [x] A saved `erro_04` Product has all information necessary for Issue 01 to render every dynamic label field; a missing required field is rejected with an actionable error.
- [x] Exactly 16 complete PD027032 Table 1 rows are available as Erro 04 Products with the supplied UPC, SKU, Supplier PN, packed quantity, and description values.
- [x] The incomplete `NYS6248` row is not created and is documented as pending source data.
- [x] Catalog and packing-station tests demonstrate that the configured H/K prefix is used rather than deriving cable type from SKU or description text.

## Blocked by

- [01-erro-04-reference-print-path.md](01-erro-04-reference-print-path.md)

