from bluesky.plans import DeltaScanPlan
from bluesky.callbacks import LiveTable, LivePlot


assert sclr.channels.chan3.connected
assert dif_beam.connected

subs = [LiveTable(['eta', 'sclr_ch3', 'dif_beam_stats5_total']),
        LivePlot('dif_beam_stats5_total', 'eta')]

RE(DeltaScanPlan([sclr.channels.chan3, dif_beam], eta, -1, 1, 3), subs)
