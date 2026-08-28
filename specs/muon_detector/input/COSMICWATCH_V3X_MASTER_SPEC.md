# CosmicWatch v3X — Archived Engineering Specification and LLM Context

## 0. Document control

- **Purpose:** canonical, LLM-readable engineering baseline for reproducing CosmicWatch v3X and designing a larger system around it.
- **Upstream project:** `spenceraxani/CosmicWatch-Desktop-Muon-Detector-v3X`
- **Archived Git commit:** `ade742d77e8be6e7f53b5547c4778736e3eef4cc`
- **Archive date:** 2026-08-28 UTC
- **Upstream license:** Creative Commons Attribution-NonCommercial 4.0 International.
- **Commercial constraint:** personal and educational building/modification are allowed; commercial use and redistribution require explicit author permission.
- **Authority rule:** values copied from upstream are facts; anything labeled `DESIGN TARGET`, `PROPOSED`, `INFERENCE`, `OPEN`, or `VERIFY` is not an upstream guarantee.
- **Canonical source:** the accompanying `upstream/` directory is the byte-for-byte source snapshot. This document is an index and normalized interpretation, not a replacement for the original drawings, firmware, manuals, or datasheets.

## 1. System definition

CosmicWatch v3X is a compact, self-contained scintillation detector optimized for cosmic-ray muons and related ionizing-radiation measurements. A `50 × 50 × 10 mm` plastic scintillator converts deposited particle energy to optical photons. An onsemi `MICROFC-60035-SMT-TR` silicon photomultiplier (SiPM) converts the photons into a fast electrical pulse. The main PCB provides SiPM bias, analog signal conditioning, hardware triggering, peak detection, ADC readout, coincidence I/O, environmental/inertial sensing, display, storage, and USB communication. A Raspberry Pi Pico/RP2040 executes acquisition and presentation firmware.

The device can operate alone or as a two-detector telescope. One detector records all local triggers; with a straight-through CAT5/6 connection, events shared within the coincidence window are flagged. The raw SiPM waveform is independently exposed at a BNC connector for oscilloscope or external fast acquisition.

## 2. Published performance baseline

| Parameter | v3X baseline |
|---|---:|
| Effective scintillator area | `25 cm²` |
| Scintillator | `50 × 50 × 10 mm` plastic |
| SiPM photosensitive area | `36 mm²` |
| Controller | RP2040 / Raspberry Pi Pico |
| CPU | Dual-core Cortex-M0+, `133 MHz` |
| Flash / RAM | `2 MB` / `264 KB` |
| ADC | 12-bit, `0–4095`, externally referenced to `2.5 V` |
| Power | approximately `0.5 W`, USB-powered |
| Maximum event rate | approximately `700 Hz` |
| Typical dead time | approximately `400 µs/event` (example measurement: `408 µs`) |
| Analog RMS noise | approximately `0.1 mV` |
| Minimum trigger threshold | approximately `4 mV` |
| SiPM bias | nominal `30.0 V`; placement sheet also calls it `29.5 V`—verify assembled board |
| SiPM supply requirement | stable, low-ripple bias above approximately `24.5 ± 0.2 V` |
| Amplifier voltage gain | approximately `13.5 V/V` (`22.6 dB`) |
| Amplifier bandwidth | approximately `10 MHz` |
| Coincidence window | `3 µs` in the instruction manual |
| Accidental coincidence | published values vary by document revision; example-measurement table gives `6.0×10⁻⁶ Hz`, paper search copy gives `4.5×10⁻⁵ Hz`; calculate for actual rates/window |
| Dry mass | approximately `110 g` |
| Nominal detector parts cost | upstream sheet: `$104.72` one-detector extended cost including listed optional/test items; approximately `$92.60` at ten-unit pricing |
| Practical one-off cost | upstream warns approximately `$200` because of minimum purchases, shipping, tax, and bulk-only materials |

Performance values are characterization results, not production acceptance tolerances. Establish explicit tolerances during our derivative design.

## 3. Functional architecture

### 3.1 Detection head

1. A charged particle deposits energy in the plastic scintillator.
2. The scintillator emits photons.
3. Aluminum foil provides a reflective wrap; black electrical tape provides optical isolation.
4. Optical gel and/or an optional `0.3 mm` silicone pad couples the scintillator face to the SiPM.
5. The SiPM is reverse-biased from the board's high-voltage rail and produces a fast current pulse.

The scintillator mounting pattern is four holes on a `30 mm × 30 mm` square. The placement sheet specifies a `#48` drill (`1.93 mm`) and four `#2 × 3/8 in` stainless screws. Preserve a clean optical interface, correct SiPM orientation, reflective coverage, and complete ambient-light exclusion.

### 3.2 Power and references

- USB powers the Raspberry Pi Pico and board.
- `MAX5026` plus `47 µH` inductor, Schottky diode, precision feedback network, filtering, and decoupling boost the system rail to nominally `30 V` for the SiPM.
- `LM4040-2.5` provides the `2.5 V` ADC reference and circuit bias reference.
- Bring-up checkpoints:
  - Verify `2.5 V` across `C25` after installing the Pico/reference section.
  - Verify approximately `+30 V` from `HV` to `GND` at the six-pin SiPM header after building the boost section.

### 3.3 Analog signal path

- Raw SiPM output is routed directly to the rear BNC for nanosecond-scale observation.
- The same pulse is AC-coupled into a `TPH2502` operational-amplifier channel.
- The non-inverting amplifier has approximately `13.5 V/V` gain and about `10 MHz` bandwidth.
- A nominal `25 mV` DC bias moves the AC-coupled signal away from the negative rail.
- A high-pass function near `3 kHz` rejects low-frequency baseline movement.
- `TP1` exposes the amplified waveform.
- A Schottky peak detector captures pulse height; a second amplifier buffers it.
- A divider maps the held peak to the ADC's `0–2.5 V` range.
- `TP2` exposes the peak-detector output.
- A comparator produces the hardware trigger when the amplified waveform exceeds the configured threshold.
- The instruction manual describes the comparator output as approximately `4.5 V` while asserted. Confirm Pico input protection/actual schematic behavior before modifying this path.

### 3.4 Acquisition sequence

On a local hardware trigger, the firmware:

1. Asserts/sends the coincidence output.
2. Searches for a coincidence input within the defined window.
3. Samples the held peak with the ADC (upstream states a single sample is about `2 µs`).
4. Deasserts coincidence output.
5. Captures an event timestamp.
6. Resets the peak detector.
7. Collects event and sensor metadata.
8. Emits the record to USB serial and/or the buffered microSD path.
9. Updates the OLED and performs background tasks.

The firmware records cumulative dead time. Correct exposure is `livetime = elapsed runtime − cumulative dead time`; count rate is `counts / livetime`.

### 3.5 Coincidence mode

- Physical link: RJ45 connectors and a **straight-through** CAT5/6 cable, `15 cm` or longer.
- The RJ45 connection also allows one powered detector to power the second according to the instruction manual. Treat this as an electrical constraint: do not connect two independent sources until the pinout and power-sharing behavior have been reviewed.
- Startup indication: both detectors flash the bright LED for approximately one second when they recognize coincidence mode.
- A local trigger is marked coincident if the peer signal arrives within approximately `3 µs`.
- Coincidence improves charged-particle selection but is not synonymous with a perfectly pure muon sample. Accidental coincidences, electromagnetic shower particles, muon bundles, and other penetrating particles remain possible.

### 3.6 Peripherals and user interfaces

- Raspberry Pi Pico / RP2040 MCU.
- `128 × 64` yellow/blue OLED; ground must be an outer pin and the exact module pin order matters.
- BMP280 `3.3 V` temperature/pressure module.
- MPU-6050 accelerometer/gyroscope module.
- Magnetic buzzer.
- 3 mm and 5 mm LEDs.
- Reset switch.
- microSD socket; upstream recommends exFAT and at least `4 GB`.
- USB serial for live streaming/programming/power.
- BNC raw-signal output.
- RJ45 coincidence/power interface.

## 4. Event data contract

### 4.1 Logical schema

Records are tab-delimited plain text, one event per line. Comment/header lines start with `#`. The GUI documents this logical order:

```text
Event
Timestamp[s]
Coincident[bool]
ADC[0-4095]
SiPM[mV]
Deadtime[s]
Temp[C]
Pressure[Pa]
Accel(X:Y:Z)[g]
Gyro(X:Y:Z)[deg/sec]
Name
Time
Date
```

Interpretation:

- `Event`: monotonic event/count identifier within a run.
- `Timestamp[s]`: detector-relative timestamp.
- `Coincident[bool]`: `1` if peer coincidence was observed, otherwise `0`.
- `ADC[0-4095]`: 12-bit sample of the buffered peak-detector output, referenced to `2.5 V`.
- `SiPM[mV]`: firmware-calculated SiPM pulse height derived from ADC calibration.
- `Deadtime[s]`: cumulative dead time since detector start, not merely per-event dead time.
- `Temp[C]`, `Pressure[Pa]`: BMP280 observations.
- `Accel`, `Gyro`: MPU-6050 vectors.
- `Name`: configured detector identity.
- `Time`, `Date`: computer-derived fields may be present in USB-captured files; onboard SD data lacks an authoritative real-time clock unless extended.

Files contain roughly `48–100 bytes/event`, depending on acquisition route and metadata. Upstream estimates `1 GB` for roughly one month and recommends a card larger than `4 GB`. Validate the actual rate and row length for our deployment.

### 4.2 Compatibility rules for software built around it

- Ignore unknown comment lines beginning with `#`.
- Parse by header names where available, not only fixed column positions.
- Preserve raw lines and original files immutably.
- Store detector identity, firmware version, configuration, source filename, ingestion timestamp, parsing version, and checksum alongside normalized events.
- Accept both onboard-SD and USB-host timestamp variants.
- Never infer absolute UTC from detector-relative time without an explicit synchronization record.
- Treat ADC-to-mV calibration as versioned metadata.
- Treat threshold, dead-time model, and coincidence window as run configuration.

## 5. Firmware and configuration baseline

- Archived binary: `Firmware/CosmicWatch_v3X.1.1.52.uf2`.
- Upstream note for `1.1.52`: OLED readout position moves every minute to reduce burn-in.
- Installation: hold `BOOTSEL` while attaching the Pico by data-capable micro-USB; release, then copy the UF2 to the mounted Pico drive. The board reboots automatically.
- The repository snapshot contains a compiled UF2 but no corresponding firmware source tree. Therefore this archive is **not fully source-reproducible firmware**.
- Threshold can be adjusted through `configure.txt` on the microSD card according to the project paper/manual. The exact accepted keys and grammar must be recovered from the firmware behavior/documentation before automation; do not invent them.
- The firmware should be treated as an opaque upstream component until source or a clean-room replacement is obtained.

## 6. Host software baseline

### 6.1 Minimal recorder

`Data/import_data.py` records USB serial output and adds a host-computer timestamp. It requires `pyserial`, prompts for a serial port, and writes received lines.

### 6.2 GUI

`GUI/GUI.py` supports live acquisition and loading existing text files. Runtime baseline is Python `3.8+` with PyQt5, pyqtgraph, numpy, scipy, matplotlib, pyserial, numpy-stl, Pillow, PyOpenGL, and optional PyOpenGL_accelerate.

Supported analyses/plots:

- Rate in counts/minute, with bins of `30, 60, 120, 180, 240, 600 s` or custom duration.
- ADC spectrum.
- Calculated SiPM voltage spectrum.
- Pressure and temperature versus time.
- Linear acceleration and angular velocity.
- Dead time.
- Rate distribution with Poisson fit.
- Inter-event-time distribution with exponential fit.
- Two-variable correlation plots with linear fit and Pearson `r`, except incompatible rate-vs-per-event combinations.
- ADC minimum filter from `0–4095` for rejecting low-amplitude events during analysis.

The GUI source and scripts are reference implementations, not a stable API. Our surrounding system should ingest the text contract directly and keep GUI integration optional.

## 7. Normalized bill of materials

The authoritative purchasing and placement sheets are included unchanged. The condensed list below exists for planning; do not use it alone for PCB assembly.

### 7.1 Main PCB electronics

| Group | Upstream parts |
|---|---|
| Resistors | `1 kΩ ×8`; `1.3 kΩ ×1`; `2 kΩ ×1`; `100 Ω`—sheet conflict, see §11; `0 Ω ×1`; `10 kΩ ×1`; `154 kΩ 0.1% 0603 ×1`; `6.65 kΩ 0.1% 0603 ×1`; `100 kΩ ×3`; `49.9 Ω ×1`; `620 Ω ×1`; `22.1 kΩ ×1`; `10 Ω ×1` |
| Capacitors | `4.7 µF 50 V 0805 ×5`; `1 µF 50 V 0805 ×7`; `0.1 µF 50 V 0805 ×6`; `200 pF 0805 ×2`; `10 pF C0G/NP0 0805 ×2`; `10 nF X7R 0805 ×2` |
| Power/reference | MAX5026; `47 µH` SMD inductor; BAT54WS; 2N7002; ferrite bead; LM4040-2.5 |
| Analog | TPH2502 dual op amp ×2; BAT54S dual Schottky ×2 |
| Compute/storage | Raspberry Pi Pico RP2040; raw microSD socket |
| Connectors | six-pin `2×3`, 2.54 mm SiPM socket; right-angle 50 Ω BNC; right-angle 8P8C/RJ45 |
| UI/sensors | reset switch; magnetic buzzer; BMP280-3.3 V; MPU-6050; 3 mm LED; 5 mm LED; 128×64 OLED |

### 7.2 Detector head and mechanics

| Item | Specification |
|---|---|
| SiPM | onsemi `MICROFC-60035-SMT-TR` |
| SiPM board header | `2×3`, 2.54 mm SMT, Molex `0015910060` in purchasing sheet |
| Scintillator | `50×50×10 mm`; four `1.93 mm` holes on 30 mm square |
| Reflector | approximately `15×15 cm` aluminum foil |
| Optical coupling | small amount (`<1 mL`) optical gel; optional `0.3 mm` silicone pad |
| Light seal | black electrical tape |
| Standoffs | two, `1/8 in` hex, `7/16 in` length, `0-80`; McMaster `91780A029` |
| Standoff screws | four, `0-80 × 1/4 in`; McMaster `91771A055` |
| Scintillator screws | four, #2 × `3/8 in`; McMaster `90065A079` |

### 7.3 Optional/test/enclosure items

- Straight-through CAT5/6 coincidence cable.
- BNC test/readout cable.
- microSD card, exFAT, recommended `≥4 GB`.
- Aluminum split-body enclosure `2506-2.9`.
- Laser-cut acrylic faceplates from `Enclosure/Faceplates.zip`, upstream purchasing sheet says `100 × 150 × 2.5 mm` stock.
- 3 mm/5 mm LED holders and `8 × 4 mm` rubber feet.

### 7.4 Exact part numbers captured upstream

The spreadsheet associates examples including `311-1.00KCRCT-ND`, `RMCF0805FT1K30DKR-ND`, `311-2.00KCRCT-ND`, `RMCF0805FT100RCT-ND`, `YAG1534CT-ND`, `P6.65KDBCT-ND`, `LM4040C25FTA`, `2648-SC0915TR-ND`, `587-2456-1-ND`, `5399-2N7002CT-ND`, `5503-TPH2502-SRCT-ND`, `MAX5026EUT+TCT-ND`, `5272-BAT54WSCT-ND`, `1212-1229-ND`, `4878-BAT54SCT-ND`, `WM5514-ND`, and `MICROFC-60035-SMT-TR`. Links, pricing, alternates, package descriptions, and all reference designators remain in the archived spreadsheets and extracted CSV context.

## 8. Assembly and bring-up sequence

1. Separate the SiPM PCB from the main PCB panel.
2. Populate passives, ferrite, LM4040, and Pico in the placement-sheet order.
3. Power temporarily and verify `2.5 V` across `C25`; disconnect power.
4. Populate the boost converter section, observing orientation and precision feedback parts.
5. Power temporarily and verify approximately `30 V` between `HV` and `GND` at the six-pin header; disconnect power.
6. Populate analog amplification, peak detector, comparator, and BNC sections.
7. If a known-good detector head is available, check the BNC for roughly `10 mV`, `200 ns` raw pulses and inspect test points with an oscilloscope. These are diagnostic expectations, not formal tolerances.
8. Populate reset, RJ45, buzzer, sensors, LEDs, OLED, and bottom-side microSD socket.
9. Flash the archived UF2 using Pico BOOTSEL.
10. Populate the SiPM PCB last, carefully identifying SiPM pin 1 from the datasheet.
11. Wrap scintillator in foil while leaving the optical coupling area exposed.
12. Apply minimal optical gel/pad, mechanically attach the SiPM PCB, and fully light-seal with black tape.
13. Install standoffs, connect the six-pin boards, slide into enclosure rails, and install faceplates.
14. Perform standalone count, coincidence, storage, USB, sensor, display, and dark/light-leak tests.

Electrostatic precautions, polarity/orientation checks, current-limited power, magnified inspection, and staged voltage verification are required good practice even where upstream language is informal.

## 9. Acceptance-test baseline for our build

The following are **proposed acceptance tests**, derived from upstream behavior and intended to make our derivative repeatable:

| Test | Acceptance concept |
|---|---|
| Source integrity | Every archived source file matches `SOURCE_MANIFEST.sha256` |
| Visual PCB inspection | Correct values/orientation; no bridges, tombstones, opens, damaged pads |
| Reference rail | `2.5 V` at `C25`; define tolerance after measuring reference/device limits |
| SiPM bias | stable nominal ~`30 V`; quantify ripple and allowed range before production |
| Dark/light seal | count/baseline does not jump when enclosure is exposed to bright ambient light |
| Raw pulse | recognizable fast negative/positive waveform per schematic/test method at BNC |
| Analog chain | TP1 gain and TP2 peak behavior correspond to injected calibrated pulse |
| ADC | valid `0–4095` output with no clipping for accepted operating range |
| Trigger | reliable threshold crossing; noise-trigger rate characterized |
| Standalone rate | plausible stable sea-level rate after threshold selection; record geometry/location |
| Coincidence | peer detection indication, flags present, cable orientation correct |
| Storage | sustained writes, valid headers/rows, safe recovery after power loss |
| USB | sustained serial stream without malformed/lost records at expected rates |
| Sensors | plausible BMP280 and MPU-6050 values with units confirmed |
| Dead time | cumulative field monotonic and derived live time non-negative |
| Reproducibility | calibration/configuration/firmware/hash stored with each run |

Do not use radioactive check sources without a separate radiation-safety procedure.

## 10. Scientific interpretation constraints

- A single detector sees muons plus environmental radioactive backgrounds and other shower components.
- Upstream cites a typical total rate around a few hertz for this geometry; one example records `2.423 ± 0.005 Hz`, with coincidence `0.315 ± 0.002 Hz` for its geometry. These are examples, not universal acceptance values.
- Coincidence geometry changes solid-angle acceptance and therefore measured rate.
- Atmospheric pressure, temperature, altitude, shielding/overburden, orientation, solar modulation, and local radioactivity affect observations.
- Correct all rates for live time.
- For randomness, arrival times may supply physical entropy, but raw event timing is not automatically a cryptographic random number generator. A derivative RNG requires a threat model, independent high-resolution timestamping, bias/correlation testing, health tests, conditioning/extraction, entropy estimation, failure behavior, and protection against environmental or injected-event manipulation.

## 11. Known conflicts, omissions, and risks

1. **Firmware source absent:** only UF2 binary is archived. This blocks deterministic builds, code audit, exact configuration grammar recovery, and long-term maintenance.
2. **100 Ω BOM discrepancy:** purchasing list says quantity `7` but names six designators (`R9,R29,R28,R8,R18,R13`); placement sheet says `R28` and `R29` were removed in PCB v28 and populates `R9,R8,R18,R13` (four total). The PCB v28 Gerbers/placement sheet must govern assembly; reconcile before ordering.
3. **Bias wording:** sources use `29.5 V` and `30.0 V`. Measure/set by schematic, feedback tolerances, and SiPM operating point.
4. **Accidental coincidence value differs among published snapshots:** recompute from actual singles rates and the actual coincidence implementation/window.
5. **Cost ages quickly:** spreadsheet prices and retail URLs are not procurement guarantees.
6. **Vendor substitutions:** OLED and sensor breakout pinouts are not universally interchangeable even when sold under the same generic name.
7. **RJ45 is not Ethernet:** never connect the detector coincidence jack to an Ethernet switch/NIC/PoE source.
8. **Shared power over RJ45:** review schematic and define safe single-/dual-power rules before building arrays.
9. **microSD resilience:** raw socket/media and firmware buffering need power-loss and filesystem-corruption testing for unattended operation.
10. **No RTC/GNSS:** absolute timestamps from SD-only acquisition are not trustworthy without an added timebase/synchronization design.
11. **License:** the upstream NonCommercial license matters if the surrounding platform becomes a product or paid service.

## 12. Interfaces for the system we build around it

### 12.1 Preserve unchanged

- Detector physics package: scintillator, optical interface, SiPM, light seal.
- Known-good analog front end and PCB as the reference instrument.
- Raw BNC output for independent validation.
- Original text output stored immutably.
- Coincidence capability, while isolating it from real Ethernet infrastructure.

### 12.2 Recommended wrapper boundaries

- **Power module:** regulated USB supply, current monitoring, reset control, optional battery/UPS.
- **Acquisition gateway:** serial ingestion, reconnect logic, raw-file rotation, checksums, monotonic receive timestamps.
- **Time module:** GNSS PPS/PTP-capable clock or local oscillator characterization for timing-sensitive work.
- **Metadata service:** detector ID, location, orientation, altitude, firmware hash, configuration, calibration, environmental state.
- **Data plane:** append-only raw archive plus normalized event stream.
- **Health plane:** rate, noise/threshold proxy, dead-time fraction, sensor plausibility, SD/USB errors, light leak, supply state.
- **Entropy plane (if pursued):** isolated extractor and health monitor; never expose unconditioned detector timing as trusted random bytes.
- **Fleet plane:** provisioning, configuration/version inventory, dashboards, alerting, and calibration history.

### 12.3 Proposed normalized event envelope

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

This is a proposed wrapper schema, not an upstream record format.

## 13. LLM operating instructions

When this bundle is supplied to an LLM, give it these rules:

1. Treat `upstream/` and file hashes as evidence; cite source file and section for factual claims.
2. Separate `UPSTREAM FACT`, `DERIVED`, `PROPOSED`, and `UNKNOWN` in every engineering answer.
3. Never silently resolve conflicting values. State the conflict and the test or authoritative artifact that resolves it.
4. Never claim firmware is open/auditable when only the UF2 is present.
5. Never treat the RJ45 coincidence connector as Ethernet.
6. Never equate all triggers or all coincidences with muons.
7. Never claim detector timing is cryptographically secure randomness without an entropy design and validation.
8. For PCB population, use PCB v28 Gerbers, circuit diagram, placement sheet, component photos, and exact package/orientation information together.
9. Preserve upstream licensing and attribution in derivatives.
10. Add decisions to a derivative-design ledger instead of rewriting upstream facts.

Suggested initial prompt:

```text
You are the systems engineer for a derivative of CosmicWatch v3X. This archive is the immutable reference baseline. Read COSMICWATCH_V3X_MASTER_SPEC.md first, then SOURCE_INDEX.md, then inspect the specific upstream files relevant to the task. Label statements as UPSTREAM FACT, DERIVED, PROPOSED, or UNKNOWN. Cite archived paths. Do not invent firmware settings, pinouts, tolerances, BOM substitutions, or performance guarantees. Surface conflicts and propose verification tests. Preserve the original detector as a reference instrument while designing external modules around stable electrical and data boundaries.
```

## 14. Archive map

- `COSMICWATCH_V3X_MASTER_SPEC.md` — this normalized baseline.
- `SOURCE_INDEX.md` — source inventory, provenance, and routing notes.
- `SOURCE_MANIFEST.sha256` — cryptographic file manifest.
- `LLM_FULL_CONTEXT.txt` — concatenated readable repository text, extracted PDFs/spreadsheets, and code for single-context ingestion.
- `upstream/` — complete pinned upstream working tree excluding `.git` history.
- `extracted/` — text extracted from PDFs and CSV renderings of the two workbooks.

## 15. Immediate engineering decisions still required

1. Define our actual mission: scientific logging, distributed monitoring, entropy collection, education, or a combination.
2. Decide whether to retain the opaque `1.1.52` firmware or replace it with auditable firmware.
3. Reconcile PCB-v28 BOM quantities against Gerbers/schematic before purchasing.
4. Establish measured rail/threshold/noise/pulse acceptance tolerances on one golden unit.
5. Define time synchronization and absolute timestamp accuracy.
6. Define array topology without abusing the RJ45 electrical interface.
7. Define raw-data retention, normalized schema, calibration records, and fleet health metrics.
8. If randomness is a goal, write the entropy-source threat model and validation plan before writing an RNG service.
