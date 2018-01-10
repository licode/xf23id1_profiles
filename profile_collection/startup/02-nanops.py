from ophyd.epics_motor import EpicsMotor
from ophyd.device import Component as Cpt
from ophyd.signal import EpicsSignal
from epics import caget,caput


class NanoMotor(EpicsMotor):
    user_setpoint = Cpt(EpicsSignal, 'PA_sm')

np_tx = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr', name='np_tx')
np_ty = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr', name='np_ty')
np_tz = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr', name='np_tz')

np_bx = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr', name='np_bx')
np_by = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr', name='np_by')
np_bz = NanoMotor('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr', name='np_bz')



# Velocity (tested 0.5, 0.1, 0.05, 0.01)

## ZP setup
#np_tx.configure(dict(velocity=.01))
#np_ty.configure(dict(velocity=.01))
#np_tz.configure(dict(velocity=.01))
#np_bx.configure(dict(velocity=.01))
#np_by.configure(dict(velocity=.01))
#np_bz.configure(dict(velocity=.01))

# standard setup  # this was 0.30 but AB tried scanning with larger step
# size and had difficulty in that bluesky will never trigger the
# cube_beam because bsui is waiting on this to move??
np_tx.configure(dict(velocity=.10))
np_ty.configure(dict(velocity=.10))
np_tz.configure(dict(velocity=.10))
np_bx.configure(dict(velocity=.10))
np_by.configure(dict(velocity=.10))
np_bz.configure(dict(velocity=.10))


# Settling time (tested 0.1 - 0.3)
#np_tx.settle_time = 0.2 ## DON'T use this as apparently it is not working

temp_settle_time = 0.2
caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.DLY',temp_settle_time)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.DLY',temp_settle_time)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.DLY',temp_settle_time)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.DLY',temp_settle_time)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.DLY',temp_settle_time)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.DLY',temp_settle_time)


# Readback dead band (tested 1.0[!!], 10e-5)

caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.RDBD',1e-5)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.RDBD',1e-5)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.RDBD',1e-5)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.RDBD',1e-5)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.RDBD',1e-5)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.RDBD',1e-5)


# Readback mode (tested 1)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.RMOD',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.RMOD',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.RMOD',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.RMOD',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.RMOD',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.RMOD',1)


# PID ON = 1

caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.CNEN',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.CNEN',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.CNEN',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.CNEN',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.CNEN',1)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.CNEN',1)


# PID proportional and integral band

caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.PCOF',0.10)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.PCOF',0.10)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.PCOF',0.10)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.PCOF',0.10)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.PCOF',0.10)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.PCOF',0.10)

caput('XF:23ID1-ES{Dif:Nano-Ax:TopX}Mtr.ICOF',0.010)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopY}Mtr.ICOF',0.010)
caput('XF:23ID1-ES{Dif:Nano-Ax:TopZ}Mtr.ICOF',0.010)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmX}Mtr.ICOF',0.010)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmY}Mtr.ICOF',0.010)
caput('XF:23ID1-ES{Dif:Nano-Ax:BtmZ}Mtr.ICOF',0.010)




BlueskyMagics.positioners += [np_tx, np_ty, np_tz, np_bx, np_by, np_bz]

sd.baseline += [np_tx, np_ty, np_tz, np_bx, np_by, np_bz]
