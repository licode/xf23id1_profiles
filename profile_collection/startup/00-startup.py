import logging

from ophyd.commands import *


from databroker import DataBroker as db, get_events, get_images, get_table

import bluesky.qt_kicker  # make matplotlib qt backend play nice with bluesky asyncio

import asyncio
from functools import partial
from functools import partial
from bluesky.standard_config import *
from bluesky.global_state import abort, stop, resume, all_is_well, panic
from bluesky.plans import *
from bluesky.callbacks import *
from bluesky.broker_callbacks import *
from bluesky.scientific_callbacks import plot_peak_stats
from bluesky.hardware_checklist import *
from bluesky import qt_kicker   # provides the libraries for live plotting
qt_kicker.install_qt_kicker()    # installs the live plotting libraries
setup_ophyd()

# Set up default metadata.
gs.RE.md['group'] = ''
gs.RE.md['config'] = {}
gs.RE.md['beamline_id'] = 'CSX-1'


# alias
RE = gs.RE


# Add a callback that prints scan IDs at the start of each scan.
def print_scan_ids(name, start_doc):
    print("Transient Scan ID: {0}".format(start_doc['scan_id']))
    print("Persistent Unique Scan ID: '{0}'".format(start_doc['uid']))

gs.RE.subscribe('start', print_scan_ids)

# Set up the logbook.
LOGBOOKS = ['Data Acquisition']
import bluesky.callbacks.olog
from pyOlog import SimpleOlogClient
simple_olog_client = SimpleOlogClient()
generic_logbook_func = simple_olog_client.log
configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

from bluesky.callbacks.olog import logbook_cb_factory
cb = logbook_cb_factory(configured_logbook_func)
RE.subscribe('start', cb)

logbook = simple_olog_client  # this is for ophyd.commands.get_logbook

# Turn off "noisy" debugging.
loop = asyncio.get_event_loop()
loop.set_debug(False)


# Define a convenient 'checklist' function.
checklist = partial(basic_checklist, ca_url='http://xf23id-ca.cs.nsls2.local:4800',
                    disk_storage=[('/', 1e9)],
                    # pv_names=['XF:23ID1-ES{Dif-Ax:SY}Pos-SP'],
                    pv_conditions=[('XF:23ID-PPS{Sh:FE}Pos-Sts', 'front-end shutter is open', assert_pv_equal, 0),
                    		   ('XF:23IDA-PPS:1{PSh}Pos-Sts', 'upstream shutter is open', assert_pv_equal, 0),
                                   ('XF:23ID1-PPS{PSh}Pos-Sts', 'downstream shutter is open', assert_pv_equal, 0)],
		   )


asc = ascan  # alias


## Uncomment this to unleash a torrent of debug messages from ophyd.
#logging.basicConfig(level=logging.DEBUG)
#import ophyd.areadetector.filestore_mixins
#ophyd.areadetector.filestore_mixins.logger.setLevel(logging.DEBUG)
