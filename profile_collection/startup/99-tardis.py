from ophyd import Component as Cpt
from ophyd import (PseudoSingle, EpicsMotor, SoftPositioner, Signal)
from hkl.diffract import E6C


# TODO: fix upstream!!
class NullMotor(SoftPositioner):
    @property
    def connected(self):
        return True


class Tardis(E6C):
    h = Cpt(PseudoSingle, '')
    k = Cpt(PseudoSingle, '')
    l = Cpt(PseudoSingle, '')

    theta = Cpt(EpicsMotor, 'XF:31IDA-OP{Tbl-Ax:X1}Mtr')
    omega = Cpt(NullMotor)
    chi =   Cpt(NullMotor)
    phi =   Cpt(NullMotor)
    delta = Cpt(EpicsMotor, 'XF:31IDA-OP{Tbl-Ax:X5}Mtr')
    gamma = Cpt(EpicsMotor, 'XF:31IDA-OP{Tbl-Ax:X6}Mtr')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prime the 3 null-motors with initial values
        # otherwise, position == None --> describe, etc gets borked
        self.omega.move(0.0)
        self.chi.move(0.0)
        self.phi.move(0.0)


# FIXME: hack to get around what should have been done at init of tardis_calc instance
# tardis_calc._lock_engine = True

# tardis = Tardis('', name='tardis', calc_inst=tardis_calc, energy=tardis_calc.energy)
tardis = Tardis('', name='tardis')

# re-map Tardis' axis names onto what an E6C expects
name_map = {'mu': 'theta', 'omega': 'omega', 'chi': 'chi', 'phi': 'phi', 'gamma': 'delta', 'delta': 'gamma'}
tardis.calc.physical_axis_names = name_map

tardis.calc.engine.mode = 'lifting_detector_mu'

# from this point, we can configure the Tardis instance
from hkl.util import Lattice

# lengths are in Angstrom, angles are in degrees
lattice = Lattice(a=9.069, b=9.069, c=10.390, alpha=90.0, beta=90.0, gamma=120.0)

# add the sample to the calculation engine
tardis.calc.new_sample('esrf_sample', lattice=lattice)

# we can alternatively set the energy on the Tardis instance
tardis.calc.wavelength = 1.61198 # angstroms

# apply some constraints

# Theta
theta = tardis.calc['theta']
theta.limits = (-181, 181)
theta.value = 0
theta.fit = True

# we don't have it. Fix to 0
phi = tardis.calc['phi']
phi.limits = (0, 0)
phi.value = 0
phi.fit = False

# we don't have it. Fix to 0
chi = tardis.calc['chi']
chi.limits = (0, 0)
chi.value = 0
chi.fit = False

# we don't have it!! Fix to 0
omega = tardis.calc['omega']
omega.limits = (0, 0)
omega.value = 0
omega.fit = False

# Attention naming convention inverted at the detector stages!
# delta
delta = tardis.calc['delta']
delta.limits = (-5, 180)
delta.value = 0
delta.fit = True

# gamma
gamma = tardis.calc['gamma']
gamma.limits = (-5, 180)
gamma.value = 0
gamma.fit = True

# add two, known reflections and compute UB
r1 = tardis.calc.sample.add_reflection(3, 3, 0,
                           position=tardis.calc.Position(delta=64.449, theta=25.285, chi=0.0, phi=0.0, omega=0.0, gamma=-0.871))

r2 = tardis.calc.sample.add_reflection(5, 2, 0,
                           position=tardis.calc.Position(delta=79.712, theta=46.816, chi=0.0, phi=0.0, omega=0.0, gamma=-1.374))

tardis.calc.sample.compute_UB(r1, r2)

# test computed real positions against the table below
# recall, lambda is 1.61198 A now
# ex:
# print(tardis.calc.forward((4,4,0)))
# print(tardis.calc.forward((4,1,0)))
#
# Experimentally found reflections @ Lambda = 1.61198 A
# (4, 4, 0) = [90.628, 38.373, 0, 0, 0, -1.156]
# (4, 1, 0) = [56.100, 40.220, 0, 0, 0, -1.091]
# @ Lambda = 1.60911
# (6, 0, 0) = [75.900, 61.000, 0, 0, 0, -1.637]
# @ Lambda = 1.60954
# (3, 2, 0) = [53.090, 26.144, 0, 0, 0, -.933]
# (5, 4, 0) = [106.415, 49.900, 0, 0, 0, -1.535]
# (4, 5, 0) = [106.403, 42.586, 0, 0, 0, -1.183]


