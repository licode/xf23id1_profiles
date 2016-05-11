from bluesky.plans import Count
from bluesky.callbacks import LiveTable, LivePlot


assert diag6_monitor.connected
assert sclr.connected


RE(Count([diag6_monitor, sclr]), LiveTable(['sclr_ch2', 'diag6_monitor']))
