from bluesky.plans import DeltaScanPlan
from bluesky.callbacks import LiveTable, LivePlot


assert sclr.channels.chan3.connected

subs = [LiveTable(['eta', 'sclr_ch3']), LivePlot('sclr_ch3', 'eta')]
RE(DeltaScanPlan([sclr.channels.chan3], eta, -1, 1, 3), subs)
