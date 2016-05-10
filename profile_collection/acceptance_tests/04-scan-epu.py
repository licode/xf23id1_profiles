from bluesky.plans import DeltaScanPlan
from bluesky.callbacks import LiveTable, LivePlot


assert epu2.connected

RE(DeltaScanPlan([epu2], epu2.gap, -0.2, 0, 5), LiveTable([epu2]))
