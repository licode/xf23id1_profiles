from bluesky.plans import Count
from bluesky.callbacks import LiveTable, LivePlot


RE(Count([diag6_monitor, sclr]), LiveTable(['sclr_ch2', 'diag6_monitor']))
