Status: completed

# Erro 04 Production Run controls

## What to build

Complete the Erro 04 operator workflow on the weight-scale station. Before its first print, the operator must provide both PO Number and Lot Number. They may change either value while the station remains active; each newly printed Carton stores the values effective at that print, while already printed Cartons remain unchanged.

The station must communicate the 0-10 kg initial Weight Tolerance and 5 kg target, enforce the tolerance before a Carton ID is allocated, and retain the Erro policy that failed/damaged labels consume a number rather than permitting Reprint.

## Acceptance criteria

- [x] An `erro_04` weigh-and-print action is blocked until both PO Number and Lot Number are supplied.
- [x] Editing PO Number or Lot Number after a successful print affects only future Cartons; historical Carton snapshots and their print payloads do not change.
- [x] The station displays the configured target and tolerance and rejects a Weight Reading outside the Product's valid range without allocating a Carton SN.
- [x] An Erro 04 Carton cannot be reprinted through either UI or API; a subsequent eligible print allocates the next shared sequence instead.
- [x] Frontend and backend tests cover required inputs, mutable session values, immutable Carton snapshots, tolerance gating, and the no-Reprint rule.

## Blocked by

- [01-erro-04-reference-print-path.md](01-erro-04-reference-print-path.md)

