from ophyd import (PVPositioner, EpicsMotor, EpicsSignal, EpicsSignalRO,
                   PVPositionerPC, Device)
from ophyd import Component as Cpt


# Diffo angles

delta = EpicsMotor('XF:23ID1-ES{Dif-Ax:Del}Mtr', name='delta')
gamma = EpicsMotor('XF:23ID1-ES{Dif-Ax:Gam}Mtr', name='gamma')
theta = EpicsMotor('XF:23ID1-ES{Dif-Ax:Th}Mtr', name='theta')


# Sample positions

sx = EpicsMotor('XF:23ID1-ES{Dif-Ax:X}Mtr', name='sx')

sy = SamplePosVirtualMotor('XF:23ID1-ES{Dif-Ax:SY}', name='sy')
sz = SamplePosVirtualMotor('XF:23ID1-ES{Dif-Ax:SZ}', name='sz')
say = EpicsMotor('XF:23ID1-ES{Dif-Ax:Y}Mtr', name='say')
saz = EpicsMotor('XF:23ID1-ES{Dif-Ax:Z}Mtr', name='saz')

cryoangle = Cryoangle('', name='cryoangle')


# Nano-positioners

nanop = Nanopositioner('XF:23ID1-ES{Dif:Lens', name='nanop')


# Diagnostic Axis

es_diag1_y = EpicsMotor('XF:23ID1-ES{Diag:1-Ax:Y}Mtr', name='es_diag1_y')
eta = EpicsMotor('XF:23ID1-ES{Diag:1-Ax:Eta}Mtr', name='eta')


# Lakeshore 336 Temp Controller

temp_sp = Lakeshore336('XF:23ID1-ES{TCtrl:1-Out:1}')
#, name='temp_sp', put_complete=True)



# Current-Voltage meter, driven in current mode

sm = VIMeter('XF:23ID1-ES{K2611:1}', name='sm')


#sm_i = PVPositioner('XF:23ID1-ES{K2611:1}Val:RB-I',name='sm_i')
#	('XF:23ID1-ES{K2611:1}Val:SP-I',
#                  readback='XF:23ID1-ES{K2611:1}Val:RB-I',
#                  stop_val=1, put_complete=True,
#                  settle_time=0.5,
#                  name='sm_i')


#sm_v = PVPositioner('XF:23ID1-ES{K2611:1}Val:SP-E',
#                  readback='XF:23ID1-ES{K2611:1}Val:RB-E',
#                  stop_val=1, put_complete=True,
#                  settle_time=0.5,
#                  name='sm_v')


#sm_r = PVPositioner('XF:23ID1-ES{K2611:1}Val:SP-R',
#                  readback='XF:23ID1-ES{K2611:1}Val:RB-R',
#                  stop_val=1, put_complete=True,
#                  name='sm_r')
