from functools import partial
from pyOlog import SimpleOlogClient
from bluesky.callbacks.olog import logbook_cb_factory

# Set up the logbook. This configures bluesky's summaries of
# data acquisition (scan type, ID, etc.).

LOGBOOKS = ['Data Acquisition']  # list of logbook names to publish to
simple_olog_client = SimpleOlogClient()
generic_logbook_func = simple_olog_client.log
configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

# This is for ophyd.commands.get_logbook, which simply looks for
# a variable called 'logbook' in the global IPython namespace.
logbook = simple_olog_client

cb = logbook_cb_factory(configured_logbook_func)

def fault_tolerant_olog(name, doc):
    try:
        cb(name, doc)
    except Exception as exc:
        print('olog error ignored:', exc)

# RE.subscribe('start', fault_tolerant_olog)  ## olog problem -> uncomment when it will
# stop hunging..
