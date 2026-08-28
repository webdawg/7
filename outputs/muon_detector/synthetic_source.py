#!/usr/bin/env python3
"""
Synthetic CosmicWatch v3X event stream.

Emits SYNTHETIC test data only, in the exact tab-delimited text contract
documented in specs/muon_detector/input/COSMICWATCH_V3X_MASTER_SPEC.md
section 4.1. This is not real detector output and must never be presented
as such downstream — its purpose is exercising ingest_gateway.py before
real hardware exists (see specs/muon_detector/SPEC.md "Implementation
notes").

Rates are loosely modeled on the archive's cited EXAMPLE measurement
(total ~2.423 Hz, coincident ~0.315 Hz for its geometry — section 10),
not a claimed universal acceptance value.
"""
import argparse
import random
import sys
import time

HEADER_COLUMNS = [
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


def make_event(event_num, t_s, cumulative_deadtime_s, name):
    coincident = random.random() < (0.315 / 2.423)
    adc = random.randint(200, 4095)
    sipm_mv = round(adc * (100.0 / 4095.0), 3)  # placeholder linear scale, not a real calibration
    deadtime_s = round(cumulative_deadtime_s, 6)
    temp_c = round(20.0 + random.uniform(-1.5, 1.5), 2)
    pressure_pa = round(101325 + random.uniform(-200, 200), 1)
    accel = ":".join(f"{v:.3f}" for v in (random.uniform(-0.05, 0.05) for _ in range(2))) + f":{1.0 + random.uniform(-0.02, 0.02):.3f}"
    gyro = ":".join(f"{random.uniform(-2, 2):.3f}" for _ in range(3))
    now = time.gmtime()
    time_str = time.strftime("%H:%M:%S", now)
    date_str = time.strftime("%Y-%m-%d", now)

    fields = [
        str(event_num),
        f"{t_s:.6f}",
        "1" if coincident else "0",
        str(adc),
        f"{sipm_mv:.3f}",
        f"{deadtime_s:.6f}",
        f"{temp_c:.2f}",
        f"{pressure_pa:.1f}",
        accel,
        gyro,
        name,
        time_str,
        date_str,
    ]
    return "\t".join(fields)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rate-hz", type=float, default=2.423, help="mean total event rate (Hz)")
    parser.add_argument("--count", type=int, default=0, help="number of events to emit (0 = run forever)")
    parser.add_argument("--name", default="SYNTHETIC-01", help="synthetic detector name")
    parser.add_argument("--realtime", action="store_true", help="sleep between events to match --rate-hz in wall-clock time")
    args = parser.parse_args()

    print(f"# schema: cosmicwatch.synthetic.v1 (SYNTHETIC TEST DATA, not real device output)")
    print("#" + "\t".join(HEADER_COLUMNS))
    sys.stdout.flush()

    event_num = 0
    t_s = 0.0
    cumulative_deadtime_s = 0.0
    emitted = 0

    while args.count == 0 or emitted < args.count:
        dt = random.expovariate(args.rate_hz)
        t_s += dt
        cumulative_deadtime_s += 400e-6  # matches archive's ~400 microsecond typical dead time
        line = make_event(event_num, t_s, cumulative_deadtime_s, args.name)
        print(line)
        sys.stdout.flush()
        event_num += 1
        emitted += 1
        if args.realtime:
            time.sleep(dt)


if __name__ == "__main__":
    main()
