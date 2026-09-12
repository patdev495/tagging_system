Status: completed

# Erro 04 BarTender and scanner acceptance

## What to build

Perform a production-device acceptance run for the completed Erro 04 flow. Confirm that the canonical `erro_04.btw` file binds the nine agreed Named SubStrings, that the physical 100 x 100 mm label follows PD027032, and that all printed Code 128 values scan back exactly as sent by the system.

## Acceptance criteria

- [x] BarTender confirms bindings for `UPC`, `SKU`, `CartonID`, `SupplierPN`, `PO`, `Date`, `Qty`, `Rev`, and `SKUDescription`; text and barcode instances of the same field match.
- [x] A printed test label matches the PD027032 layout, including 100 x 100 mm size, readable vertical Carton ID, and required quiet zones.
- [x] A physical scanner reads every barcode on the test label and each result exactly matches the stored Carton print data.
- [x] The acceptance record includes the printer, BarTender version, scanner model, test Product, generated Carton SN, and any remedial template changes.

## Blocked by

- [01-erro-04-reference-print-path.md](01-erro-04-reference-print-path.md)
- [02-erro-04-catalog-and-product-seed.md](02-erro-04-catalog-and-product-seed.md)
- [03-erro-04-production-run-controls.md](03-erro-04-production-run-controls.md)
