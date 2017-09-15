
from ophyd.device import (Component as C, DynamicDeviceComponent as DDC)
from ophyd import (EpicsScaler, EpicsSignal, EpicsSignalRO, Device, SingleTrigger, HDF5Plugin,
                           ImagePlugin, StatsPlugin, ROIPlugin, TransformPlugin)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector import ADComponent, EpicsSignalWithRBV
from ophyd.areadetector.plugins import PluginBase, ProcessPlugin
from ophyd import Component as Cpt
from ophyd import AreaDetector
from bluesky.examples import NullStatus
from collections import OrderedDict
import bluesky.plans as bp


def _setup_stats(cam_in):
    for k in (f'stats{j}' for j in range(1, 6)):
        cam_in.read_attrs.append(k)
        getattr(cam_in, k).read_attrs = ['total']


# Ring current

# TODO Make this a Device so it can be used by bluesky.
ring_curr = EpicsSignalRO('XF:23ID-SR{}I-I', name='ring_curr')

# TODO Make this a Device so it can be used by bluesky.
diag6_monitor = EpicsSignal('XF:23ID1-BI{Diag:6-Cam:1}Stats1:Total_RBV',
                            name='diag6_monitor')


# #selected for beam position only with no image filtering
# diag6_raw4 = EpicsSignal('XF:23ID1-BI{Diag:6-Cam:1}Stats4:Total_RBV',
#                            name='diag6_raw4')

#TODO move this to diag6 area detector

diag6_pid_threshold = EpicsSignal('XF:23ID1-BI{Diag:6-Cam:1}Stats1:CentroidThreshold',name =  'diag6_pid_threshold')

#
mono_tempa = EpicsSignalRO('XF:23ID1-OP{TCtrl:1-Chan:A}T-I',
                         name='mono_tempa')

mono_tempb = EpicsSignalRO('XF:23ID1-OP{TCtrl:1-Chan:B}T-I',
                         name='mono_tempb')

mono_tempc = EpicsSignalRO('XF:23ID1-OP{TCtrl:1-Chan:C}T-I', name='mono_tempc')

mono_tempd = EpicsSignalRO('XF:23ID1-OP{TCtrl:1-Chan:D}T-I', name='mono_tempd')


grt1_temp = EpicsSignalRO('XF:23ID1-OP{Mon-Grt:1}T-I',
                        name='grt1_temp')

grt2_temp = EpicsSignalRO('XF:23ID1-OP{Mon-Grt:2}T-I',
                        name='grt2_temp')

# FCCD sensor temperature
fccd_temp = EpicsSignalRO('XF:23ID1-ES{TCtrl:2-Chan:A}T:C-I', name='fccd_temp')

# Utility water temperature after mixing valve
#uw_temp = EpicsSignal('UT:SB1-Cu:1{}T:Spply_Ld-I', name='uw_temp')


# Calculated BPMs for combined EPUs
angX = EpicsSignalRO('XF:23ID-ID{BPM}Val:AngleXS-I', name='angX')

angY = EpicsSignalRO('XF:23ID-ID{BPM}Val:AngleYS-I', name='angY')

# EPU1 positions for commissioning
epu1_x_off = EpicsSignalRO('SR:C31-{AI}23:FPGA:x_mm-I', name='epu1_x_off')

epu1_x_ang = EpicsSignalRO('SR:C31-{AI}23:FPGA:x_mrad-I', name='epu1_x_ang')

epu1_y_off = EpicsSignalRO('SR:C31-{AI}23:FPGA:y_mm-I', name='epu1_y_off')

epu1_y_ang = EpicsSignalRO('SR:C31-{AI}23:FPGA:y_mrad-I', name='epu1_y_ang')


# EPU2 positions for commissioning
epu2_x_off = EpicsSignalRO('SR:C31-{AI}23-2:FPGA:x_mm-I', name='epu2_x_off')

epu2_x_ang = EpicsSignalRO('SR:C31-{AI}23-2:FPGA:x_mrad-I', name='epu2_x_ang')

epu2_y_off = EpicsSignalRO('SR:C31-{AI}23-2:FPGA:y_mm-I', name='epu2_y_off')

epu2_y_ang = EpicsSignalRO('SR:C31-{AI}23-2:FPGA:y_mrad-I', name='epu2_y_ang')


# CSX-1 Scalar

def _scaler_fields(attr_base, field_base, range_, **kwargs):
    defn = OrderedDict()
    for i in range_:
        attr = '{attr}{i}'.format(attr=attr_base, i=i)
        suffix = '{field}{i}'.format(field=field_base, i=i)
        defn[attr] = (EpicsSignalRO, suffix, kwargs)

    return defn


class PrototypeEpicsScaler(Device):
    '''SynApps Scaler Record interface'''

    # tigger + trigger mode
    count = C(EpicsSignal, '.CNT', trigger_value=1)
    count_mode = C(EpicsSignal, '.CONT', string=True)

    # delay from triggering to starting counting
    delay = C(EpicsSignal, '.DLY')
    auto_count_delay = C(EpicsSignal, '.DLY1')

    # the data
    channels = DDC(_scaler_fields('chan', '.S', range(1, 33)))
    names = DDC(_scaler_fields('name', '.NM', range(1, 33)))

    time = C(EpicsSignal, '.T')
    freq = C(EpicsSignal, '.FREQ')

    preset_time = C(EpicsSignal, '.TP')
    auto_count_time = C(EpicsSignal, '.TP1')

    presets = DDC(_scaler_fields('preset', '.PR', range(1, 33)))
    gates = DDC(_scaler_fields('gate', '.G', range(1, 33)))

    update_rate = C(EpicsSignal, '.RATE')
    auto_count_update_rate = C(EpicsSignal, '.RAT1')

    egu = C(EpicsSignal, '.EGU')

    def __init__(self, prefix, *, read_attrs=None, configuration_attrs=None,
                 name=None, parent=None, **kwargs):
        if read_attrs is None:
            read_attrs = ['channels', 'time']

        if configuration_attrs is None:
            configuration_attrs = ['preset_time', 'presets', 'gates',
                                   'names', 'freq', 'auto_count_time',
                                   'count_mode', 'delay',
                                   'auto_count_delay', 'egu']

        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)

        self.stage_sigs.update([(self.count_mode, 0)])


sclr = PrototypeEpicsScaler('XF:23ID1-ES{Sclr:1}', name='sclr')
for sig in sclr.channels.signal_names:
    getattr(sclr.channels, sig).name = 'sclr_' + sig.replace('an', '')


def sclr_to_monitor_mode(sclr, count_time):
    # remeber sclr.auto_count_delay
    yield from bp.mv(sclr.auto_count_time, count_time)
    yield from bp.mv(sclr.auto_count_update_rate, 0)
    yield from bp.mv(sclr.count_mode, 'AutoCount')


class Temperature(Device):
    a = Cpt(EpicsSignalRO, '-Chan:A}T-I')
    b = Cpt(EpicsSignalRO, '-Chan:B}T-I')


temp = Temperature('XF:23ID1-ES{TCtrl:1', name='temp')


class StandardCam(SingleTrigger, AreaDetector):
    stats1 = Cpt(StatsPlugin, 'Stats1:')
    stats2 = Cpt(StatsPlugin, 'Stats2:')
    stats3 = Cpt(StatsPlugin, 'Stats3:')
    stats4 = Cpt(StatsPlugin, 'Stats4:')
    stats5 = Cpt(StatsPlugin, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    proc1 = Cpt(ProcessPlugin, 'Proc1:')


class NoStatsCam(SingleTrigger, AreaDetector):
    pass


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    # AD v2.2.0 (at least) does not have this. It is present in v1.9.1.
    file_number_sync = None

    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()


class ProductionCamBase(AreaDetector):
    # # Trying to add useful info..
    stats1 = Cpt(StatsPlugin, 'Stats1:')
    stats2 = Cpt(StatsPlugin, 'Stats2:')
    stats3 = Cpt(StatsPlugin, 'Stats3:')
    stats4 = Cpt(StatsPlugin, 'Stats4:')
    stats5 = Cpt(StatsPlugin, 'Stats5:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')
    trans1 = Cpt(TransformPlugin, 'Trans1:')

    proc1 = Cpt(ProcessPlugin, 'Proc1:')
    #proc2 = Cpt(ProcessPlugin, 'Proc2:')

    # This does nothing, but it's the right place to add code to be run
    # once at instantiation time.
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

    def pause(self):              #Dan Allen added to make bsui stop progress bar on ^C
        self.cam.acquire.put(0)
        super().pause()


class ProductionCamStandard(SingleTrigger, ProductionCamBase):

    hdf5 = Cpt(HDF5PluginWithFileStore,
               suffix='HDF1:',
               write_path_template='/GPFS/xf23id/xf23id1/fccd_data/%Y/%m/%d/',
               root='/GPFS/xf23id/xf23id1/',
               reg=db.reg)

    def stop(self):
        self.hdf5.capture.put(0)
        return super().stop()

    def pause(self):
        self.hdf5.capture.put(0)
        return super().pause()

    def resume(self):
        self.hdf5.capture.put(1)
        return super().resume()


class TestCam(SingleTrigger, AreaDetector):
    "writes data to test driectory"
    hdf5 = Cpt(HDF5PluginWithFileStore,
               suffix='HDF1:',
               write_path_template='/GPFS/xf23id/xf23id1/test_data/%Y/%m/%d/',
               root='/GPFS/xf23id/xf23id1/',
               reg=db.reg)
    # The trailing '/' is essential!!


diag3 = StandardCam('XF:23ID1-BI{Diag:3-Cam:1}', name='diag3')
# this is for the cube diag for now (es_diag_cam_2)
# diag5 = StandardCam('XF:23ID1-BI{Diag:5-Cam:1}', name='diag5')
diag6 = NoStatsCam('XF:23ID1-BI{Diag:6-Cam:1}', name='diag6')


# for aligning im MuR mode - TODO replace PV with better description
cube_beam = StandardCam('XF:23ID1-BI{Diag:5-Cam:1}', name='cube_beam')

_setup_stats(cube_beam)

dif_beam = StandardCam('XF:23ID1-ES{Dif-Cam:Beam}', name='dif_beam')
# fs1 = StandardCam('XF:23IDA-BI:1{FS:1-Cam:1}', name='fs1')

_setup_stats(dif_beam)

# Princeton CCD camera

# pimte = AreaDetectorFileStorePrinceton('XF:23ID1-ES{Dif-Cam:PIMTE}',
#                                        file_path='/GPFS/xf23id/xf23id1/pimte_data/',
#                                       ioc_file_path='x:/xf23id1/pimte_data/',
#                                       name='pimte')

class FastShutter(Device):
    shutter = Cpt(EpicsSignal, 'XF:23ID1-TS{EVR:1-Out:FP0}Src:Scale-RB',
                  write_pv='XF:23ID1-TS{EVR:1-Out:FP0}Src:Scale-SP')
    # TODO THIS POLARITY IS JUST A GUESS -- CHECK!!

    def open(self):
        self.shutter.put(1)

    def close(self):
        self.shutter.put(0)


fccd = ProductionCamStandard('XF:23ID1-ES{FCCD}', name='fccd')
fccd.read_attrs = ['hdf5']
fccd.hdf5.read_attrs = []
fccd.configuration_attrs = ['cam.acquire_time',
                            'cam.acquire_period',
                            'cam.image_mode',
                            'cam.num_images']
_setup_stats(fccd)
# to not break downstream analysis yet
fccd.read_attrs.append('cam.acquire_time')
fccd.read_attrs.append('cam.acquire_period')
fccd.read_attrs.append('cam.num_images')


# CM commented on 2017_07_05 due to connection error preventing BSUI to
# start suitably..
#
# # Test CCD
#
# ccdtest = TestCam('XF:23ID1-ES{Tst-Cam:1}', name='ccdtest')

import time as ttime
import epics
import numpy as np


class WaveformCollector:
    def __init__(self, name, pv_basename, data_is_time=True):
        self.root = self
        self.parent = None
        self._name = name
        self._pv_basename = pv_basename
        self._pv_sel = epics.PV("{}Sw-Sel".format(pv_basename))
        self._pv_rst = epics.PV("{}Rst-Sel".format(pv_basename))
        self._pv_wfrm_n = epics.PV("{}Val:TimeN-I".format(pv_basename),
                                   auto_monitor=False)
        self._pv_wfrm = epics.PV("{}Val:Time-Wfrm".format(pv_basename),
                                 auto_monitor=False)
        self._pv_wfrm_nord = epics.PV(
            "{}Val:Time-Wfrm.NORD".format(pv_basename),
            auto_monitor=False)
        self._cb = None
        self._data_is_time = data_is_time
        self.done = True
        self.success = True

    def _get_wfrm(self):
        if self._pv_wfrm_n.get():
            return self._pv_wfrm.get(count=int(self._pv_wfrm_nord.get()))
        else:
            return None

    def kickoff(self):
        self._pv_sel.put(2, wait=True)  # Put us in reset mode
        self._pv_rst.put(1, wait=True)  # Trigger processing
        self._pv_sel.put(1, wait=True)  # Start Buffer
        return self

    @property
    def finished_cb(self):
        return self._cb

    @finished_cb.setter
    def finished_cb(self, cb):
        if self._cb is not None:
            raise RuntimeError("Cannot change the callback")
        if self.done:
            cb()
        else:
            self._cb = cb

    def complete(self):
        return NullStatus()

    def _finish(self):
        self.ready = True
        if self._cb is not None:
           self._cb()
           self._cb = None

    def collect(self):
        self.stop()
        payload = self._get_wfrm()
        if payload is None:
           return

        for i, v in enumerate(payload):
           if self._data_is_time:
                x = v
           else:
                x = i
           ev = {'data': {self._name: x},
                 'timestamps': {self._name: v},
                 'time': v}
           yield ev

    def stop(self):
        self._pv_sel.put(0, wait=True)  # Stop Collection

    def describe_collect(self):
        return {
            self._name: {
                self._name: {
                    'source': self._pv_basename,
                    'dtype': 'number',
                    'shape': None,
                }
            }
        }


topoff_inj = WaveformCollector('topoff_inj', 'XF:23ID1-SR{TO-Inj}',
                               data_is_time=False)
topoff_btr = WaveformCollector('topoff_btr', 'XF:23ID1-SR{TO-BS}',
                               data_is_time=False)
fccd_time = WaveformCollector('fccd_time', 'XF:23ID1-ES{FCCD-TS}')


class AreaDetectorTimeseriesCollector:
    def __init__(self, name, pv_basename, num_points=1000000):
        self.root = self
        self.parent = None
        self._name = name
        self._pv_basename = pv_basename
        self._num_points = num_points

        self._pv_tscontrol = epics.PV("{}TSControl".format(pv_basename))
        self._pv_num_points = epics.PV("{}TSNumPoints".format(pv_basename))
        self._pv_cur_point = epics.PV("{}TSCurrentPoint".format(pv_basename))
        self._pv_wfrm = epics.PV("{}TSTotal".format(pv_basename),
                                 auto_monitor=False)
        self._pv_wfrm_ts = epics.PV("{}TSTimestamp".format(pv_basename),
                                    auto_monitor=False)
        self._cb = None
        self.done = True
        self.success = True

    def stage(self):
        print("staging %s" % self._name)

    def unstage(self):
        print("unstaging %s" % self._name)

    def _get_wfrms(self):
        n = self._pv_cur_point.get()
        if n:
            return (self._pv_wfrm.get(count=n), self._pv_wfrm_ts.get(count=n))
        else:
            return (np.array([]), np.array([]))

    def kickoff(self):
        # self._pv_num_points.put(self._num_points, wait=True)
        # Erase buffer and start collection
        self._pv_tscontrol.put(0, wait=True)
        return self

    def complete(self):
        return NullStatus()

    @property
    def finished_cb(self):
        return self._cb

    @finished_cb.setter
    def finished_cb(self, cb):
        if self._cb is not None:
            raise RuntimeError("Cannot change the callback")
        if self.done:
            cb()
        else:
            self._cb = cb

    def _finish(self):
        self.ready = True
        if self._cb is not None:
            self._cb()
            self._cb = None

    def collect(self):
        self.stop()
        payload_val, payload_time = self._get_wfrms()
        if payload_val.size == 0:
            # We have no data, yeild {}
            ev = {'data': {self._name: 0.0},
                  'timestamps': {self._name: 0.0},
                  'time': ttime.time()}
            yield ev
        for v, t in zip(payload_val, payload_time):
            ev = {'data': {self._name: v},
                  'timestamps': {self._name: t},
                  'time': ttime.time()}
            yield ev

    def stop(self):
        self._pv_tscontrol.put(2, wait=True)  # Stop Collection

    def describe_collect(self):
        return {
            self._name: {
                self._name: {
                    'source': self._pv_basename,
                    'dtype': 'number',
                    'shape': None,
                }
            }
        }


diag6_flyer1 = AreaDetectorTimeseriesCollector(
    'diag6_flyer1', 'XF:23ID1-BI{Diag:6-Cam:1}Stats1:', num_points=100000000)
diag6_flyer5 = AreaDetectorTimeseriesCollector(
    'diag6_flyer5', 'XF:23ID1-BI{Diag:6-Cam:1}Stats5:', num_points=100000000)
fccd_flyer5 = AreaDetectorTimeseriesCollector(
    'fccd_flyer5', 'XF:23ID1-ES{FCCD}Stats5:', num_points=100000000)
fccd_flyer1 = AreaDetectorTimeseriesCollector(
    'fccd_flyer1', 'XF:23ID1-ES{FCCD}Stats1:', num_points=100000000)

# pimte_cam = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}cam1:Amecquire_RBV',
#                         write_pv='XF:23ID1-ES{Dif-Cam:PIMTE}cam1:Acquire',
#                         rw=True, name='pimte_cam_trigger')
# pimte_tot1 = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}Stats1:Total_RBV',
#                          rw=False, name='pimte_tot1')
# pimte_tot2 = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}Stats2:Total_RBV',
#                          rw=False, name='pimte_tot2')
# pimte_tot3 = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}Stats3:Total_RBV',
#                          rw=False, name='pimte_tot3')
# pimte_tot4 = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}Stats4:Total_RBV',
#                          rw=False, name='pimte_tot4')
# pimte_tot5 = EpicsSignal('XF:23ID1-ES{Dif-Cam:PIMTE}Stats5:Total_RBV',
#                          rw=False, name='pimte_tot5')


# Saturn interface for Vortex MCA detector
vortex = Vortex('XF:23ID1-ES{Vortex}', name='vortex')
# vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time']
vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time', 'mca.rois']
vortex.mca.read_attrs.append('rois')
vortex.mca.rois.read_attrs = ['roi0', 'roi1', 'roi2', 'roi3', 'roi4']
# gs.TABLE_COLS = ['vortex_mca_rois_roi4_count']; gs.PLOT_Y = 'vortex_mca_rois_roi4_count'
