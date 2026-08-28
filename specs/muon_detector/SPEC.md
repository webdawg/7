# Muon Detector

**Status:** in-progress
**Part of:** [7 — The City of Light](../../SPEC.md)
**Hardware baseline:** [`input/COSMICWATCH_V3X_MASTER_SPEC.md`](input/COSMICWATCH_V3X_MASTER_SPEC.md)
(archived CosmicWatch v3X reference — see `DESIGN_LEDGER.md` for how we're
building against it)
**Implementation:** [`outputs/muon_detector/`](../../outputs/muon_detector/)
(this repo, for now — see `creation.md` convention for when that changes)

## Purpose

The first physical sensory input for the simulated City of Light. Where most
of 7's mythology deals in *already-recorded* human data, a muon detector is
different in kind: it is a live, real-world channel that produces genuinely
new data, continuously, for free, independent of any human network — a
literal signal falling out of the sky.

## Why muons

- Muons are secondary cosmic ray particles, produced when primary cosmic
  rays (mostly high-energy protons from outside the solar system) collide
  with nuclei in the upper atmosphere, ~15 km up.
- At sea level, muon flux is roughly 1 muon per cm² per minute, arriving
  from all directions, day and night, everywhere on Earth.
- Muons have a proper lifetime of ~2.2 microseconds — by classical physics
  they shouldn't survive the trip to the ground at all. That they routinely
  do is a direct, tabletop-observable demonstration of relativistic time
  dilation. Every detected muon is a small, free physics experiment.
- Thematically, this ties directly to root [SPEC.md](../../SPEC.md)'s idea
  of "entangled solar light" and messengers from deeper structure: muons are
  actual particles from beyond Earth, arriving continuously, asking nothing
  of any network to do it. They are the most literal, least metaphorical
  version of 7's "aperture" function available with off-the-shelf hardware.

## Physical device

**UPSTREAM FACT** (from the archived baseline — see `DESIGN_LEDGER.md` for
labeling convention): a `50×50×10 mm` plastic scintillator, optically
coupled to an onsemi `MICROFC-60035-SMT-TR` SiPM, reverse-biased at nominal
~30 V. An RP2040 (Raspberry Pi Pico) handles triggering, ADC peak sampling,
and event emission. Two units can be cabled together (straight-through
CAT5/6, RJ45 — **not Ethernet**, never connect to networking infrastructure)
for hardware coincidence within a ~3 µs window.

This is CosmicWatch v3X, archived and pinned rather than paraphrased —
generic references to "CosmicWatch-style" designs in earlier drafts of this
spec are superseded by the actual baseline document. Assembly-grade
specifics (exact BOM quantities, Gerbers, pinouts) are **not yet available**
to us — see `DESIGN_LEDGER.md`'s "Archive completeness" section before
sourcing parts.

## Data schema (node output)

Superseded by the archived baseline's fully-specified contract. The real
upstream text format (tab-delimited, one event per line — see
`input/COSMICWATCH_V3X_MASTER_SPEC.md` §4.1) is normalized into the
`cosmicwatch.event.v1` JSON envelope it proposes in §12.3, implemented
unmodified by [`outputs/muon_detector/ingest_gateway.py`](../../outputs/muon_detector/ingest_gateway.py):

```json
{
  "schema": "cosmicwatch.event.v1",
  "detector_id": "stable-id",
  "run_id": "uuid",
  "source": "usb|sd",
  "source_line": "immutable original line",
  "event_number": 0,
  "detector_time_s": 0.0,
  "host_receive_time_utc": "RFC3339 timestamp or null",
  "coincident": false,
  "adc_counts": 0,
  "sipm_mv": 0.0,
  "cumulative_deadtime_s": 0.0,
  "temperature_c": null,
  "pressure_pa": null,
  "accel_g": [null, null, null],
  "gyro_deg_s": [null, null, null],
  "firmware": "1.1.52",
  "firmware_sha256": "from manifest",
  "configuration_hash": "sha256 or null",
  "calibration_id": "versioned-id or null",
  "ingest_version": "semantic version"
}
```

This replaces the earlier placeholder schema in this section (a simplified
`node_id`/`device`/`pulse_height_mv` shape) — that shape was invented before
the real upstream contract was available and doesn't match it. The 7
network's node-protocol envelope (see `../INDEX.md#node-protocol`) still
wraps identity/location fields for network routing purposes; the detector
event payload itself follows `cosmicwatch.event.v1` above.

## Network role

- Registers as node type `muon_detector` under the shared
  [node protocol](../INDEX.md#node-protocol).
- Low, steady event rate makes it a good first device for exercising the
  ingestion/streaming pipeline before higher-throughput device types are
  built. The generic "~1/cm²/min" figure used elsewhere in this repo is a
  rough sea-level estimate, not this specific geometry's rate; the archived
  baseline's own cited example for its actual detector geometry is ~2.4 Hz
  total, ~0.3 Hz coincident (an example measurement, not a universal
  acceptance value — see `DESIGN_LEDGER.md` item 4).
- The RJ45 coincidence link is physically real but electrically fragile:
  never wire it to Ethernet infrastructure, and don't power two independent
  coincidence-paired units without reviewing the shared-power behavior
  first (`DESIGN_LEDGER.md` item 6).
- Long term: many muon detectors worldwide, timestamp-synced closely
  enough, can correlate extensive air showers in real time — a genuinely
  global, physically distributed sensor grid, and a concrete first step
  toward the "devices in space" ambition, since the primary particles
  triggering these showers already originate outside Earth.

## Visualization

A core visual requirement for this device, independent of whatever
ingestion pipeline eventually exists: in the eventual City of Light
visualization, muons must read as **raining down from space, randomly** —
arriving from above at irregular intervals and slightly varied angles, not
on a beat and not from a single direction. This is not decorative; it's the
most literal, legible way to render what this device actually detects.

A first pass at this exists now at
[`outputs/vision/index.html`](../../outputs/vision/index.html) — a
self-contained static WebGL page. It currently renders **synthetic** muon
rain: spawn timing is a randomized rate (not yet a true Poisson process
matched to real flux), and each muon's fall angle is sampled from a rough
visual approximation of the real cos²(θ) zenith-angle distribution,
capped at ~36° from vertical so the rain still reads clearly as falling.

This is a placeholder for real data, not a finished simulation: once a real
or simulated `muon_detector` node emits events per the "Data schema" above,
`outputs/vision` should switch from synthetic random spawning to rendering
(or replaying) actual event streams — same visual language, real source.

## Implementation notes

**Step 1 (simulated node) is done.** Implemented in
[`outputs/muon_detector/`](../../outputs/muon_detector/):

- `synthetic_source.py` — emits synthetic events in the exact upstream
  tab-delimited text contract, Poisson-timed, clearly labeled as synthetic
  test data. Not a hardware simulator (no ADC/analog modeling) — just a
  correctly-shaped fake serial stream for exercising the gateway.
- `ingest_gateway.py` — parses that stream (or eventually real device
  serial output) by header name, preserves every raw line immutably with a
  SHA-256 checksum, and emits `cosmicwatch.event.v1` JSON. Tested against
  both well-formed and malformed input: malformed lines are preserved and
  flagged `parse_ok: false` rather than crashing the pipeline.

Run it: `python3 synthetic_source.py --count 100 | python3 ingest_gateway.py --detector-id TEST-01`

**Step 2 (real hardware) is now unblocked on paper.** The full upstream
repo has been fetched and pinned at
[`input/upstream/`](input/upstream/) (see `input/SOURCE_INDEX.md`),
including the complete Gerber set, schematic, and both BOM/purchasing
spreadsheets. The previously-flagged 100 Ω resistor discrepancy is
resolved — see `DESIGN_LEDGER.md` item 3: populate `R9, R8, R18, R13`,
not `R28`/`R29`. What remains before physical assembly:

- Order parts against the reconciled BOM (placement sheet, not the stale
  purchasing-list designator set).
- A physical build is still required to resolve `DESIGN_LEDGER.md` item 4
  (rail/threshold/noise/pulse tolerances) — having the files doesn't
  substitute for measuring a real unit.
- Firmware source genuinely does not exist upstream (confirmed by the full
  fetch, not just absent from our copy) — see `DESIGN_LEDGER.md` item 2.

## Open questions

- Coincidence window and acceptable false-positive rate for v1? (Blocked
  behind physical hardware — see `DESIGN_LEDGER.md` item 4.)
- How tightly do distributed detectors need to be time-synced (GPS? NTP?)
  to usefully correlate air showers across sites? (`DESIGN_LEDGER.md`
  item 5 — no timebase is designed yet.)
- Does the simulated node need to model geomagnetic latitude / altitude
  effects on flux, or is a flat rate good enough for v1?
- Who's sourcing/ordering parts and assembling the physical golden unit,
  and when? Everything blocking that decision on missing files is now
  resolved (see `DESIGN_LEDGER.md`); what remains is a physical build.
