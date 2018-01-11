from csx1.startup import *

from IPython import get_ipython
import nslsii

nslsii.configure_olog(get_ipython().user_ns)
