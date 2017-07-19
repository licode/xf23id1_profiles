# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

from metadatastore.mds import MDS
# from metadataclient.mds import MDS
from databroker import Broker
from databroker.core import register_builtin_handlers
from filestore.fs import FileStore

# pull from /etc/metadatastore/connection.yaml
mds = MDS({'host': 'xf23id-broker', 'database': 'datastore2',
           'port': 27017, 'timezone': 'US/Eastern'}, auth=False)
# mds = MDS({'host': CA, 'port': 7770})

# pull configuration from /etc/filestore/connection.yaml
db = Broker(mds, FileStore({'host': 'xf23id-broker',
                            'database': 'filestore',
                            'port': 27017}))

register_builtin_handlers(db.event_sources[0].fs)

get_events = db.get_events
get_images = db.get_images
get_table = db.get_table
get_fields = db.get_fields
restream = db.restream
process = db.process

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
from bluesky.global_state import gs
gs.RE.subscribe_lossless('all', db.insert)

# At the end of every run, verify that files were saved and
# print a confirmation message.
from bluesky.callbacks.broker import verify_files_saved
# gs.RE.subscribe('stop', post_run(verify_files_saved))

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.plan_tools import print_summary
from bluesky.global_state import gs, abort, stop, resume
from time import sleep
import numpy as np

RE = gs.RE  # convenience alias

# Uncomment the following lines to turn on verbose messages for
# debugging.
# import logging
# ophyd.logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG)

from bluesky.plans import *
from bluesky.callbacks.broker import *
from bluesky.callbacks.scientific import plot_peak_stats


# Set up default metadata.
# from historydict import HistoryDict
# gs.RE.md = HistoryDict(filename)
gs.RE.md['group'] = ''
gs.RE.md['config'] = {}
gs.RE.md['beamline_id'] = 'CSX-1'

# Add a callback that prints scan IDs at the start of each scan.
def print_scan_ids(name, start_doc):
    print("Transient Scan ID: {0} @ {1}".format(start_doc['scan_id'],time.strftime("%Y/%m/%d %H:%M:%S")))
    print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))

gs.RE.subscribe('start', print_scan_ids)


asc = ascan  # alias
