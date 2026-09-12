Status: completed

# Erro 04 reference print path

## What to build

Deliver one complete, demonstrable `erro_04` packing and print path for a representative CAT6A Product. A valid Weight Reading must allocate the next non-resetting, shared Erro 04 Carton Sequence; encode the Carton SN as `H|K + YMD + NNNN`; persist the Carton; and generate a BarTender job for `erro_04.btw` using the agreed nine Named SubStrings.

The `NNNN` component must be a four-character base-32 sequence using `0`-`9` and uppercase letters excluding `I`, `L`, `O`, and `U`. It is shared across `H` and `K`, never resets, starts after the highest persisted `erro_04` Carton SN, and begins at `0001` when no such Carton exists. The reference Product uses CAT6A prefix `H` and the initial 0-10 kg Weight Tolerance with a 5 kg target.

## Acceptance criteria

- [x] A Product with Template Code `erro_04` can be selected at the Erro packing station and complete a weigh-and-print request within the 0-10 kg Weight Tolerance.
- [x] The generated Carton SN uses the PD027032 year/month/day encoding and the shared base-32 `NNNN` sequence; `0009` advances to `000A`, omitted letters are never emitted, and H/K allocations share one sequence.
- [x] The print job passes `UPC`, `SKU`, `CartonID`, `SupplierPN`, `PO`, `Date`, `Qty`, `Rev`, and `SKUDescription` to `erro_04.btw`.
- [x] The Carton persists the exact data used to print, and unit tests cover serial allocation, rollover, rejection outside Weight Tolerance, and BTXML generation.
- [x] Existing `erro_01`-`erro_03` print paths remain unchanged.

## Blocked by

None - can start immediately.

