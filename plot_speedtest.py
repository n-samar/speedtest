#!/usr/bin/env python3

import matplotlib
import matplotlib.pyplot as plt
import csv
import os
import datetime
import numpy as np
import sys

plt.rcParams['lines.markersize'] = 3

time_idx = 3
ping_idx = 5
bw_down_idx = 6
bw_up_idx = 7
bits_per_Mb = 1 << 20

latency_threshold = 150  # ms
down_threshold = 10  # Mbits per second
up_threshold = 2  # Mbits per second

csvfile = open(os.path.expanduser("~/speedtest.csv"))
results = csv.reader(csvfile)
results = [ elem for elem in results ]

start_idx = 0
if len(sys.argv) > 1:
    start_idx = -int(sys.argv[1])

results = results[start_idx:]

times = [ elem[time_idx] for elem in results ]
pings = [ float(elem[ping_idx]) for elem in results ]
bw_downs = [ float(elem[bw_down_idx]) / bits_per_Mb for elem in results ]
bw_ups = [ float(elem[bw_up_idx]) / bits_per_Mb for elem in results ]

datetimes = [ datetime.datetime.strptime(elem, '%Y-%m-%dT%H:%M:%S.%f%z') for elem in times ]
date_nums = matplotlib.dates.date2num(datetimes)

ping_max = max(1.05*max(pings), latency_threshold*1.1)
bw_up_max = max(1.05*max(bw_ups), up_threshold)
bw_down_max = max(1.05*max(bw_downs), down_threshold)

fig = plt.figure()

gridspec = fig.add_gridspec(4, 3)
ax_ping = fig.add_subplot(gridspec[1, :])
ax_bw_down = fig.add_subplot(gridspec[2, :])
ax_bw_up = fig.add_subplot(gridspec[3, :])

ax_ping_cdf = fig.add_subplot(gridspec[0, 0])
ax_bw_down_cdf = fig.add_subplot(gridspec[0, 1])
ax_bw_up_cdf = fig.add_subplot(gridspec[0, 2])

ax_ping.fill_between(date_nums, latency_threshold, 5000, color="red", alpha=0.5)
ax_ping.set_xlim((min(date_nums), max(date_nums)))
ax_ping.plot_date(date_nums, pings)
ax_ping.set_title("Latency")
ax_ping.set_xlabel("Time")
ax_ping.set_ylabel("Milliseconds")
ax_ping.axhline(latency_threshold, color="red")
ax_ping.set_ylim(ymin = 0)
ax_ping.set_ylim(ymax = ping_max)

ax_bw_down.plot_date(date_nums, bw_downs)
ax_bw_down.set_xlim((min(date_nums), max(date_nums)))
ax_bw_down.fill_between(date_nums, 0, down_threshold, color="red", alpha=0.5)
ax_bw_down.set_title("Download")
ax_bw_down.set_xlabel("Time")
ax_bw_down.set_ylabel("Mbits per second")
ax_bw_down.axhline(down_threshold, color="red")
ax_bw_down.set_ylim(ymin = 0)

ax_bw_up.plot_date(date_nums, bw_ups)
ax_bw_up.set_xlim((min(date_nums), max(date_nums)))
ax_bw_up.fill_between(date_nums, 0, up_threshold, color="red", alpha=0.5)
ax_bw_up.set_title("Upload")
ax_bw_up.set_ylabel("Mbits per second")
ax_bw_up.set_xlabel("Time")
ax_bw_up.axhline(up_threshold, color="red")
ax_bw_up.set_ylim(ymin = 0)

ax_ping_cdf.scatter(sorted(pings), np.linspace(0, 1, len(pings)))
ax_ping_cdf.set_xlim(xmin = 0)
ax_ping_cdf.set_xlim(xmax = ping_max)
ax_ping_cdf.axvspan(latency_threshold, 5000, color="red", alpha=0.5)
ax_ping_cdf.axvline(x=latency_threshold, color="r")
ping_bad_ratio = sum(x > latency_threshold for x in pings)
ping_bad_percentage = int(100.0 * ping_bad_ratio / len(pings))
ax_ping_cdf.set_xlabel("Milliseconds")
ax_ping_cdf.set_title(f"Latency CDF ({ping_bad_percentage}% bad)")

ax_bw_down_cdf.scatter(sorted(bw_downs), np.linspace(0, 1, len(pings)))
ax_bw_down_cdf.set_xlim(xmin = 0)
ax_bw_down_cdf.axvspan(0, down_threshold, color="red", alpha=0.5)
bw_down_bad_ratio = sum(x < down_threshold for x in bw_downs)
bw_down_bad_percentage = int(100.0 * bw_down_bad_ratio / len(bw_downs))
ax_bw_down_cdf.set_title(f"Download CDF ({bw_down_bad_percentage}% bad)")
ax_bw_down_cdf.set_xlabel("Mbits per second")
ax_bw_down_cdf.axvline(x=down_threshold, color="r")

ax_bw_up_cdf.scatter(sorted(bw_ups), np.linspace(0, 1, len(pings)))
ax_bw_up_cdf.set_xlim(xmin = 0)
ax_bw_up_cdf.axvspan(0, up_threshold, color="red", alpha=0.5)
bw_up_bad_ratio = sum(x < up_threshold for x in bw_ups)
bw_up_bad_percentage = int(100.0 * bw_up_bad_ratio / len(bw_ups))
ax_bw_up_cdf.set_title(f"Upload CDF ({bw_up_bad_percentage}% bad)")
ax_bw_up_cdf.set_xlabel("Mbits per second")
ax_bw_up_cdf.axvline(x=up_threshold, color="r")

fig.set_size_inches(18.5, 15.5)
fig.set_dpi(100)
fig.tight_layout()

fig.savefig("plots/speedtest.pdf")
