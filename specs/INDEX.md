# Specs Index

This directory is the heart of the repo: the ground-level engineering
counterpart to the mythic/conceptual [SPEC.md](../SPEC.md) at repo root.
Where the root spec describes what 7 *is*, each spec in here describes one
real, buildable piece of it — a "device" contributing real-world compute or
data to the simulated City of Light.

## Convention

- Each device/subsystem gets its own folder: `specs/<device_slug>/`.
- That folder holds a `SPEC.md` (required) plus any number of supporting
  files — diagrams, schemas, reference code, sample data. Filenames beyond
  `SPEC.md` are otherwise unconstrained.
- Every `SPEC.md` declares a `**Status:**` of `proposed`, `in-progress`, or
  `implemented`.
- Once a spec has a real implementation, its `SPEC.md` links to the
  implementation repo(s) — specs stay conceptual/design-only; actual code
  lives elsewhere (see `creation.md` at repo root for the bootstrap
  convention new implementation repos follow).
- Every device spec should tie back to at least one theme from the root
  `SPEC.md` (custodianship, aperture, invitation, entangled inference, ...),
  explaining *why* the device belongs in the City of Light, not just what
  it technically does.

## Node protocol

Every node type — sensor or compute, passive or active — shares the same
minimal registration shape, so the network can treat wildly different
devices uniformly. This is deliberately thin; it will grow as more node
types expose requirements the current shape doesn't cover.

- **`node_id`** — unique per physical device instance (e.g.
  `muon-<site>-<n>`, `pqc-<site>-<n>`).
- **`device`** (a.k.a. node type) — the slug matching its `specs/<slug>/`
  folder, e.g. `muon_detector`, `personal_quantum_computer`.
- **`location`** — `{ lat, lon, alt_m }`. Residential nodes may round or
  fuzz this for privacy; precision requirements are unspecified for now.
- **`ts_utc`** — ISO 8601 UTC timestamp on every emitted record.
- **Registration** — how a node announces itself to the network before
  emitting data. Not yet designed: no auth, discovery, or transport is
  specified. Every node spec that reaches `in-progress` needs to either use
  a shared registration mechanism defined here, or document why it can't.
- **Emission** — per-node-type payload schema, defined in that node's own
  `SPEC.md` (see `muon_detector/SPEC.md`'s "Data schema" section for the
  current example).

This section exists because two node specs (`muon_detector`,
`personal_quantum_computer`) already reference it. Treat it as scaffolding,
not a finished protocol — auth, discovery, and transport are open and
should be resolved in a dedicated spec pass once more node types make their
shared requirements clearer.

## Registered specs

| Device | Status | Path |
|---|---|---|
| Muon detector | in-progress | [muon_detector/SPEC.md](muon_detector/SPEC.md) |
| Personal quantum computer | proposed | [personal_quantum_computer/SPEC.md](personal_quantum_computer/SPEC.md) |
