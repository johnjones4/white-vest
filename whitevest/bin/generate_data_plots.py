import argparse
import csv

import matplotlib.pyplot as plt

TIME_COL = 0
PRESSURE_COL = 1

parser = argparse.ArgumentParser(
    description="Plots altitude from a source telemetry file."
)
parser.add_argument("--input", type=str, required=True, help="Telemetry source file.")
parser.add_argument("--start", type=int, required=False, help="Start index to plot.")
parser.add_argument("--end", type=int, required=False, help="End index to plot.")
parser.add_argument(
    "--chute", type=float, required=False, help="Timestamp when the chute deploys."
)
parser.add_argument("--output", type=str, required=False, help="Output graph file.")

args = parser.parse_args()

with open(args.input, "r") as file:
    reader = csv.reader(file)
    seconds_values = []
    altitude_values = []
    velocity_values = []
    initial_pressure_reading = None
    highest_altitude = 0
    highest_altitude_seconds = 0
    max_v = 0
    max_v_seconds = 0
    last_altitude = None
    last_seconds = None
    start_seconds = 0
    for i, row in enumerate(reader):
        if (
            row
            and len(row) > 0
            and (not args.start or i >= args.start)
            and (not args.end or i <= args.end)
        ):
            if args.start and i == args.start:
                start_seconds = float(row[TIME_COL])

            seconds = float(row[TIME_COL]) - start_seconds
            seconds_values.append(seconds)

            pressure = float(row[PRESSURE_COL])
            if not initial_pressure_reading:
                initial_pressure_reading = pressure
            altitude = 44307.7 * (1 - (pressure / initial_pressure_reading) ** 0.190284)
            if altitude > highest_altitude:
                highest_altitude = altitude
                highest_altitude_seconds = seconds
            altitude_values.append(altitude)

            if last_altitude and last_seconds:
                velocity = (altitude - last_altitude) / (seconds - last_seconds)
                velocity_values.append(velocity)
                if velocity > max_v:
                    max_v = velocity
                    max_v_seconds = seconds
            else:
                velocity_values.append(0)

            last_altitude = altitude
            last_seconds = seconds
        i += 1

    fig, ax1 = plt.subplots()
    fig.set_size_inches(14, 8.5)

    color = "tab:red"
    ax1.plot(seconds_values, altitude_values, color=color)
    ax1.annotate(
        f"Apogee at {round(highest_altitude, 2)}m / {round(highest_altitude_seconds, 2)}s",
        xy=(highest_altitude_seconds, highest_altitude),
        xytext=(highest_altitude_seconds + 2, highest_altitude + 10),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )
    if args.chute:
        ax1.axvline(x=args.chute)
        ax1.text(args.chute - 0.5, 0, f"Chute deploy at {args.chute}s", rotation=90)

    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Altitude (meters)")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Velocity (meters/second)")
    ax2.annotate(
        f"Max velocity at {round(max_v, 2)}m/s / {round(max_v_seconds, 2)}s",
        xy=(max_v_seconds, max_v),
        xytext=(max_v_seconds + 2, max_v + 10),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )
    color = "tab:green"
    ax2.plot(seconds_values, velocity_values, color=color)
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()

    if args.output:
        fig.savefig(args.output)
    else:
        plt.show()
