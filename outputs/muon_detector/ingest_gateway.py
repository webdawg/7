#!/usr/bin/env python3
"""
CosmicWatch v3X acquisition gateway.

Implements the "Acquisition gateway" and "Data plane" wrapper boundaries
described in specs/muon_detector/input/COSMICWATCH_V3X_MASTER_SPEC.md
section 12.2, against the upstream text event contract in section 4.1.

Reads tab-delimited event lines from stdin (real device serial output or
synthetic_source.py), and for each line:

  1. Preserves the original raw line immutably, with a SHA-256 checksum
     (section 4.2: "Preserve raw lines and original files immutably").
  2. Parses fields by header name, not fixed column position, using the
     leading "#"-prefixed header comment line to learn column order
     (section 4.2: "Parse by header names where available").
  3. Emits the normalized cosmicwatch.event.v1 JSON envelope proposed in
     section 12.3, unmodified from the archive's proposal.

Never infers absolute UTC from detector-relative time (section 4.2):
`host_receive_time_utc` is this process's own receive-time clock, kept
separate from and never conflated with `detector_time_s`.
"""
import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone

EXPECTED_COLUMNS = [
    "Event",
    "Timestamp[s]",
    "Coincident[bool]",
    "ADC[0-4095]",
    "SiPM[mV]",
    "Deadtime[s]",
    "Temp[C]",
    "Pressure[Pa]",
    "Accel(X:Y:Z)[g]",
    "Gyro(X:Y:Z)[deg/sec]",
    "Name",
    "Time",
    "Date",
]

INGEST_VERSION = "0.1.0-derivative"


def parse_vector3(raw):
    try:
        parts = raw.split(":")
        if len(parts) != 3:
            return [None, None, None]
        return [float(p) for p in parts]
    except (ValueError, AttributeError):
        return [None, None, None]


def parse_event_line(raw_line, columns, detector_id, run_id, source):
    fields = raw_line.split("\t")
    by_name = {}
    if len(fields) == len(columns):
        by_name = dict(zip(columns, fields))

    def get_float(name):
        v = by_name.get(name)
        try:
            return float(v) if v is not None else None
        except ValueError:
            return None

    def get_int(name):
        v = by_name.get(name)
        try:
            return int(v) if v is not None else None
        except ValueError:
            return None

    def get_bool(name):
        v = by_name.get(name)
        if v is None:
            return None
        return v.strip() in ("1", "true", "True")

    parse_ok = len(by_name) > 0

    envelope = {
        "schema": "cosmicwatch.event.v1",
        "detector_id": detector_id,
        "run_id": run_id,
        "source": source,
        "source_line": raw_line,
        "source_line_sha256": hashlib.sha256(raw_line.encode("utf-8")).hexdigest(),
        "parse_ok": parse_ok,
        "event_number": get_int("Event"),
        "detector_time_s": get_float("Timestamp[s]"),
        "host_receive_time_utc": datetime.now(timezone.utc).isoformat(),
        "coincident": get_bool("Coincident[bool]"),
        "adc_counts": get_int("ADC[0-4095]"),
        "sipm_mv": get_float("SiPM[mV]"),
        "cumulative_deadtime_s": get_float("Deadtime[s]"),
        "temperature_c": get_float("Temp[C]"),
        "pressure_pa": get_float("Pressure[Pa]"),
        "accel_g": parse_vector3(by_name.get("Accel(X:Y:Z)[g]", "")),
        "gyro_deg_s": parse_vector3(by_name.get("Gyro(X:Y:Z)[deg/sec]", "")),
        "firmware": None,
        "firmware_sha256": None,
        "configuration_hash": None,
        "calibration_id": None,
        "ingest_version": INGEST_VERSION,
    }
    return envelope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--detector-id", required=True, help="stable detector identity")
    parser.add_argument("--run-id", default=None, help="run UUID (generated if omitted)")
    parser.add_argument("--source", choices=["usb", "sd"], default="usb")
    parser.add_argument("--raw-archive", default=None, help="path to append-only raw log (raw lines only, untouched)")
    args = parser.parse_args()

    run_id = args.run_id or str(uuid.uuid4())
    columns = list(EXPECTED_COLUMNS)

    raw_fh = open(args.raw_archive, "a", encoding="utf-8") if args.raw_archive else None

    parsed_count = 0
    skipped_comment_count = 0
    unparsed_count = 0

    try:
        for raw_line in sys.stdin:
            raw_line = raw_line.rstrip("\n").rstrip("\r")
            if raw_line == "":
                continue

            if raw_fh:
                raw_fh.write(raw_line + "\n")
                raw_fh.flush()

            if raw_line.startswith("#"):
                header_line = raw_line[1:]
                if "\t" in header_line:
                    candidate = header_line.split("\t")
                    if candidate == EXPECTED_COLUMNS:
                        columns = candidate
                skipped_comment_count += 1
                continue

            envelope = parse_event_line(raw_line, columns, args.detector_id, run_id, args.source)
            if not envelope["parse_ok"]:
                unparsed_count += 1
            else:
                parsed_count += 1
            print(json.dumps(envelope))
            sys.stdout.flush()
    finally:
        if raw_fh:
            raw_fh.close()

    print(
        f"# ingest summary: parsed={parsed_count} unparsed={unparsed_count} "
        f"comments_skipped={skipped_comment_count}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
