# Source Index — CosmicWatch v3X Archive

**Fetched:** 2026-08-28 UTC, from `https://github.com/spenceraxani/CosmicWatch-Desktop-Muon-Detector-v3X`
**Pinned commit:** `ade742d77e8be6e7f53b5547c4778736e3eef4cc`
("Update firmware to reduce OLED burn in. Pixels move every minute.") —
matches the commit `COSMICWATCH_V3X_MASTER_SPEC.md` §0 cites, and its commit
message independently confirms the firmware note in §5.
**Manifest:** [`SOURCE_MANIFEST.sha256`](SOURCE_MANIFEST.sha256) — every
file below, hashed.

This resolves the "Archive completeness" blocker recorded in
[`../DESIGN_LEDGER.md`](../DESIGN_LEDGER.md): the master spec's own §14
archive map named `upstream/`, `extracted/`, and this file as siblings that
were missing when the master spec was first archived. They're now present.

## `upstream/` — pinned working tree

Full upstream repository at the pinned commit, excluding `.git` history and
one excluded file (see below). 76 files, ~207 MB, dominated by the
`Firmware/*.uf2` binary, `Pictures/*.png` renders, and PDFs.

Notable contents:

- `PCB/PCB_Gerber_Files_v28.zip` — complete fabrication-ready Gerber set:
  both copper layers, soldermask, silkscreen, edge cuts, PTH/NPTH drill
  files. This is the artifact `DESIGN_LEDGER.md` item 3 and item 4 were
  blocked on.
- `PCB/Circuit_Diagram.pdf` — schematic.
- `Component_Placement_Sheet.xlsx`, `Purchasing_List_v3X_sa.xlsx` — the two
  BOM/purchasing spreadsheets referenced throughout the master spec.
  Extracted to CSV in `extracted/` (see below).
- `Firmware/CosmicWatch_v3X.1.1.52.uf2` — the same opaque compiled firmware
  cited in the master spec. `Firmware/Readme.txt` confirms only the version
  note; no firmware source is present anywhere in this tree. The master
  spec's §11.1 claim ("firmware source absent... blocks deterministic
  builds") still holds — this fetch did not change that.
- `GUI/GUI.py`, `Data/import_data.py` — the host software baseline
  described in the master spec §6.
- `Datasheets/`, `The Instruction Manual.pdf`, `The Physics Document.pdf`,
  `The Example Measurements.pdf`, `The Troubleshooting Document.pdf` —
  primary sources the master spec normalizes.

**Excluded from the copy:** `GUI/.claude/settings.local.json` — the
original author's own local Claude Code permission allowlist, referencing
their personal machine paths (`/Users/saxani/...`). Inspected before
exclusion: contains only `ls`/`chmod`/a read-only PIL image-size check on
their own files, no hooks, nothing that reaches outside their own repo
checkout. Harmless, but it's personal tooling clutter unrelated to the
detector project, so it isn't part of our pinned copy. Its hash is not in
`SOURCE_MANIFEST.sha256`.

## `extracted/` — spreadsheet CSV extractions

Both BOM/purchasing `.xlsx` workbooks, converted to CSV (all sheets) with a
small stdlib-only Python script (no `openpyxl`/`pandas` available in this
environment) since they can't be diffed or grepped directly as binary xlsx:

- `Sheet_1_-_BOM.csv` — from `Component_Placement_Sheet.xlsx` (69 rows).
- `Sheet1.csv` — from `Purchasing_List_v3X_sa.xlsx` (75 rows).

No PDF text extraction was performed (no `LLM_FULL_CONTEXT.txt` generated
here) — `pdftotext` is available if a future pass wants it, but nothing in
this session's work required it.

## Using this archive

Per `COSMICWATCH_V3X_MASTER_SPEC.md` §0's authority rule: values here are
facts (this is the primary source the master spec normalizes); the master
spec itself remains the normalized index, not a replacement for these
files. When the two disagree, these files govern — see
`DESIGN_LEDGER.md` item 3 for a worked example (the 100 Ω resistor BOM
discrepancy, resolved from `extracted/Sheet_1_-_BOM.csv` directly).
