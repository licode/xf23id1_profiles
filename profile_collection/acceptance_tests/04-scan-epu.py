from bluesky.plans import relative_scan
from bluesky.callbacks import LiveTable, LivePlot


assert epu2.connected

RE(relative_scan([epu2], epu2.gap, 0, 0.2, 5), LiveTable([epu2]))
