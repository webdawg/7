# Derivative Design Ledger — Muon Detector (CosmicWatch v3X baseline)

**Reference baseline:** [`input/COSMICWATCH_V3X_MASTER_SPEC.md`](input/COSMICWATCH_V3X_MASTER_SPEC.md)
(archived 2026-08-28, upstream commit `ade742d77e8be6e7f53b5547c4778736e3eef4cc`).

This ledger records our decisions against that baseline's §15 "Immediate
engineering decisions still required," per its own instruction (§13.10):
"Add decisions to a derivative-design ledger instead of rewriting upstream
facts." Every line is labeled **UPSTREAM FACT**, **DERIVED**, **PROPOSED**,
or **UNKNOWN/BLOCKED**, per §13.2 of the baseline.

## Archive completeness — RESOLVED

**UPSTREAM FACT.** Originally blocked: the baseline's own archive map (§14)
lists `SOURCE_INDEX.md`, `SOURCE_MANIFEST.sha256`, `upstream/`, and
`extracted/` as siblings of the master spec that were missing. Resolved by
fetching the actual upstream repo, pinned to the exact commit the master
spec cites (`ade742d77e8be6e7f53b5547c4778736e3eef4cc` — commit message
independently confirms the §5 firmware note). See
[`input/SOURCE_INDEX.md`](input/SOURCE_INDEX.md) for full contents and
[`input/SOURCE_MANIFEST.sha256`](input/SOURCE_MANIFEST.sha256) for
checksums. We now have the real Gerbers, schematic, BOM/purchasing
spreadsheets (extracted to CSV), datasheets, and the same opaque firmware
UF2 — but still **not** firmware source, which does not exist upstream
either (confirmed, not just absent from our copy). Decisions below are
updated accordingly; anything still blocked now requires either a physical
golden unit or genuinely doesn't exist upstream, not a missing download.

## Decisions

### 1. Mission

**PROPOSED.** Combination: distributed environmental monitoring (feeding
[`specs/muon_detector/SPEC.md`](SPEC.md)'s network role) plus education.
Entropy/RNG use is explicitly **not** in scope until the threat model in
baseline §10 and §15.8 is written and validated — no RNG service exists or
is planned yet.

### 2. Firmware: retain opaque `1.1.52` vs. replace

**PROPOSED, deferred.** Retain the archived opaque `1.1.52` UF2 as the
reference/golden-unit firmware for now. Confirmed, not just assumed: the
full upstream repo fetch (`input/upstream/Firmware/`) contains only the
compiled `.uf2` and a one-line readme — no firmware source exists upstream
at this commit, this isn't an artifact we're missing. We cannot responsibly
design clean-room replacement firmware without a physical board to
validate against (ADC timing, comparator behavior, peak-detector reset
timing are all analog-dependent). Revisit once a golden unit exists.

### 3. PCB-v28 BOM reconciliation (100 Ω discrepancy, §11.2)

**RESOLVED — DERIVED from primary source.** Checked directly against
[`input/extracted/Sheet_1_-_BOM.csv`](input/extracted/Sheet_1_-_BOM.csv)
(from `Component_Placement_Sheet.xlsx`) and
[`input/extracted/Sheet1.csv`](input/extracted/Sheet1.csv) (from
`Purchasing_List_v3X_sa.xlsx`):

- Purchasing list (Sheet1.csv row 13): "100 Ohm resistor", qty `7`,
  designators `R9,R29,R28,R8,R18,R13` — six designators listed against a
  quantity of seven, an internal inconsistency in that sheet on its own.
- Placement sheet (Sheet_1_-_BOM.csv): two line items populate 100 Ω
  parts — row 8 (`R9,R8,R18`) with the explicit note *"R28 and R29 were
  removed in v28"*, and row 50 (`R13`) alone. Total: four designators —
  `R9, R8, R18, R13`.

**Conclusion:** the placement sheet is authoritative and internally
consistent with its own stated design change; the purchasing list is
stale (it still includes the removed `R28`/`R29`, and even undercounts its
own designator list against its stated quantity). **Populate 100 Ω at
`R9, R8, R18, R13` only. Do not populate `R28` or `R29` with 100 Ω
resistors** — per the placement sheet, those positions were removed in v28.
This resolves the specific conflict baseline §11.2 flagged; a full
line-by-line reconciliation of the entire BOM against the Gerbers has not
been done and remains open if a complete audit is wanted before ordering.

### 4. Rail/threshold/noise/pulse acceptance tolerances

**UNKNOWN/BLOCKED — genuinely, not for lack of files.** Requires
measurement on a physical golden unit (baseline §9 "Acceptance-test
baseline"). Having the Gerbers now unblocks *building* that unit; it
doesn't substitute for measuring it. No tolerances are set here.

### 5. Time synchronization / absolute timestamp accuracy

**PROPOSED.** No absolute UTC claims from raw detector timestamps, per
baseline §4.2 ("Never infer absolute UTC from detector-relative time
without an explicit synchronization record") and §11.10 (no RTC/GNSS
onboard). Our ingestion layer (see below) records `host_receive_time_utc`
as a separate, explicitly-labeled receive-time field, never presented as
detector-side absolute time. A GNSS PPS/PTP time module remains a future,
undesigned addition (baseline §12.2 "Time module").

### 6. Array topology

**PROPOSED.** The RJ45 jack is reserved strictly for its upstream purpose —
two-detector coincidence pairing — and is never connected to Ethernet
infrastructure (baseline §11.7, a hard rule, not a style preference).
Fleet-level coordination across many nodes happens exclusively through the
software acquisition gateway (per-node USB/serial ingestion), not through
any electrical meshing of the coincidence link. Shared power over RJ45
between a coincidence pair (baseline §11.8) is treated as a real electrical
hazard until the schematic is available to review — don't wire two
independent power sources onto a coincidence pair.

### 7. Raw-data retention, normalized schema, fleet health metrics

**DERIVED — implemented now.** This is the one item in §15 fully
answerable from the text contract alone (baseline §4.1, §12.2, §12.3),
with no missing artifacts blocking it. Implemented in
[`outputs/muon_detector/`](../../outputs/muon_detector/):

- `synthetic_source.py` — emits synthetic events in the exact upstream
  tab-delimited text contract (baseline §4.1), clearly labeled synthetic,
  for testing the pipeline before real hardware exists.
- `ingest_gateway.py` — the "Acquisition gateway" (baseline §12.2): parses
  the upstream text contract by header name, preserves every raw line
  immutably alongside a checksum, and emits the normalized
  `cosmicwatch.event.v1` JSON envelope (baseline §12.3) — unmodified from
  the archive's proposed schema.

### 8. Entropy source

**UNKNOWN/BLOCKED, intentionally.** Not pursued. Baseline §10 and §15.8 are
explicit that unconditioned detector timing must never be exposed as
trusted random bytes without a written threat model, independent
timestamping, bias/correlation testing, and health tests — none of which
exist yet. No code in this repo treats detector output as an RNG.
