

from ophyd import (EpicsScaler, EpicsSignal, EpicsSignalRO, Device, SingleTrigger, HDF5Plugin,
			   ImagePlugin, StatsPlugin, ROIPlugin, TransformPlugin)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector import ADComponent, EpicsSignalWithRBV
from ophyd.areadetector.plugins import PluginBase, ProcessPlugin
from ophyd import Component as Cpt
from ophyd import AreaDetector
from bluesky.examples import NullStatus

# Ring current

# TODO Make this a Device so it can be used by bluesky.
ring_curr = EpicsSignal('XF:23ID-SR{}I-I',
                        name='ring_curr')

# TODO Make this a Device so it can be used by bluesky.
diag6_monitor = EpicsSignal('XF:23ID1-BI{Diag:6-Cam:1}Stats1:Total_RBV',
                            name='diag6_monitor')


##selected for beam position only with no image filtering
#diag6_raw4 = EpicsSignal('XF:23ID1-BI{Diag:6-Cam:1}Stats4:Total_RBV',
#                            name='diag6_raw4')

# TODO Make these a Device so it can be used in bluesky.
mono_tempa= EpicsSignal('XF:23ID1-OP{TCtrl:1-Chan:A}T-I',
                        name='mono_tempa')

mono_tempb = EpicsSignal('XF:23ID1-OP{TCtrl:1-Chan:B}T-I',
                        name='mono_tempb')

mono_tempc= EpicsSignal('XF:23ID1-OP{TCtrl:1-Chan:C}T-I',name='mono_tempc')

mono_tempd = EpicsSignal('XF:23ID1-OP{TCtrl:1-Chan:D}T-I',name='mono_tempd')



grt1_temp = EpicsSignal('XF:23ID1-OP{Mon-Grt:1}T-I',
                        name='grt1_temp')

grt2_temp = EpicsSignal('XF:23ID1-OP{Mon-Grt:2}T-I',
                        name='grt2_temp')


# Utility water temperature after mixing valve
uw_temp = EpicsSignal('UT:SB1-Cu:1{}T:Spply_Ld-I',name='uw_temp')


# Calculated BPMs for combined EPUs
angX = EpicsSignal('XF:23ID-ID{BPM}Val:AngleXS-I',name='angX')

angY = EpicsSignal('XF:23ID-ID{BPM}Val:AngleYS-I',name='angY')

#EPU1 positions for commissioning
epu1_x_off = EpicsSignal('SR:C31-{AI}23:FPGA:x_mm-I',name='epu1_x_off')

epu1_x_ang = EpicsSignal('SR:C31-{AI}23:FPGA:x_mrad-I',name='epu1_x_ang')

epu1_y_off = EpicsSignal('SR:C31-{AI}23:FPGA:y_mm-I',name='epu1_y_off')

epu1_y_ang = EpicsSignal('SR:C31-{AI}23:FPGA:y_mrad-I',name='epu1_y_ang')


#EPU2 positions for commissioning
epu2_x_off = EpicsSignal('SR:C31-{AI}23-2:FPGA:x_mm-I',name='epu2_x_off')

epu2_x_ang = EpicsSignal('SR:C31-{AI}23-2:FPGA:x_mrad-I',name='epu2_x_ang')

epu2_y_off = EpicsSignal('SR:C31-{AI}23-2:FPGA:y_mm-I',name='epu2_y_off')

epu2_y_ang = EpicsSignal('SR:C31-{AI}23-2:FPGA:y_mrad-I',name='epu2_y_ang')


# CSX-1 Scalar
from ophyd.device import (Component as C, DynamicDeviceComponent as DDC)

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

    # By defeault, FileStoreHDF5 relies on the signal hdf5.num_capture
    # to determine how many "frames" (2D images) are in a given "point"
    # (datum document in FileStore). This breaks if we capture in
    # "Stream" mode, in which hdf5.num_capture is always 0 (meaning, I
    # guess, undefined. Thanks, EPICS). We'll use a different signal.
    def get_frames_per_point(self):
        return int(self.parent.cam.num_images.get())


#class HDF5PluginWithFileStoreUsingCustomEnable(HDF5PluginWithFileStore):
#
#    # As in HDF5PluginWithFileStore, we customize how we find out how
#    # many 2D images constitute one "datum".
#    def get_frames_per_point(self):
#        return int(self.parent.plugin_num_images.get())


class TriggerUsingCustomEnable(SingleTrigger):
    """
    Do not disrupt acquisition or touch the 'acquire' signal.
    Instead, flip the custom 'enable' switch added by Stuart in
    January 2016.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._acquisition_signal = self.enable
        self.stage_sigs.pop('cam.acquire')
        self.stage_sigs.pop('cam.image_mode')
        self._acquisition_signal.subscribe(self._acquire_changed)

    def stage(self):
        if self.cam.image_mode.get(as_string=True) != 'Continuous':
            raise RuntimeError("Detector must be in Continuous before scan is begun.")
        if self.cam.trigger_mode.get(as_string=True) != 'Internal':
            raise RuntimeError("Detector trigger mode must be Internal before scan is begun.")
        if self.cam.acquire.get() != 1:
            raise RuntimeError("Detector must in be acquire mode before scan is begun.")
        super().stage()


class ProductionCamBase(AreaDetector):
    ## Trying to add useful info..
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
    proc2 = Cpt(ProcessPlugin, 'Proc2:')

    #fccdproc1 = Cpt(PluginBase, 'FastCCD1:')
    #fccdproc2 = Cpt(PluginBase, 'FastCCD2:')

    acquire_time = ADComponent(EpicsSignalWithRBV, 'cam1:AcquireTime')

    # This does nothing, but it's the right place to add code to be run
    # once at instantiation time.
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)



class ProductionCamStandard(SingleTrigger, ProductionCamBase):
    # plugin_num_images = ADComponent(EpicsSignalWithRBV, 'cam1:NumImages')
    # num_images_captured = Cpt(EpicsSignalRO, 'cam1:NumImages')  # not needed?

    hdf5 = Cpt(HDF5PluginWithFileStore,
               suffix='HDF1:',
               write_path_template='/GPFS/xf23id/xf23id1/fccd_data/%Y/%m/%d/',
               root='/GPFS/xf23id/xf23id1/',
               fs=db.event_sources[0].fs)


#class ProductionCamCustom(TriggerUsingCustomEnable, ProductionCamBase):
class ProductionCamCustom(ProductionCamBase):
    #enable = ADComponent(EpicsSignalWithRBV, 'FastCCD1:EnableOutput')

    #plugin_num_images = ADComponent(EpicsSignalWithRBV, 'FastCCD1:NumImages')  # used by FileStore to record frame_per_point

    ## The custom signal `plugin_num_images` plays the role that
    # `hdf5.num_capture` normally plays in providing 'frame_per_point'
    # to the FileStore resource document.

    # num_images_captured =  Cpt(EpicsSignalRO, 'HDF1:NumCaptured_RBV')  # not needed?

    hdf5 = Cpt(HDF5PluginWithFileStore,#UsingCustomEnable
               suffix='HDF1:',
               write_path_template='/GPFS/xf23id/xf23id1/fccd_data/%Y/%m/%d/',
               root='/GPFS/xf23id/xf23id1/',
               fs=db.event_sources[0].fs)

    def stop(self):
        self.hdf5.capture.put(0)
        super().stop()

    def pause(self):
        self.hdf5.capture.put(0)
        super().pause()


class TestCam(SingleTrigger, AreaDetector):
    "writes data to test driectory"
    hdf5 = Cpt(HDF5PluginWithFileStore,
                   suffix='HDF1:',
                   write_path_template='/GPFS/xf23id/xf23id1/test_data/%Y/%m/%d/',
                   root='/GPFS/xf23id/xf23id1/',
                   fs=db.event_sources[0].fs)
                   # The trailing '/' is essential!!


diag3 = StandardCam('XF:23ID1-BI{Diag:3-Cam:1}', name='diag3')
#diag5 = StandardCam('XF:23ID1-BI{Diag:5-Cam:1}', name='diag5') #this is for the cube diag for now (es_diag_cam_2)
diag6 = NoStatsCam('XF:23ID1-BI{Diag:6-Cam:1}', name='diag6')


# for aligning im MuR mode - TODO replace PV with better description
cube_beam = StandardCam('XF:23ID1-BI{Diag:5-Cam:1}', name='cube_beam')

cube_beam.read_attrs = ['stats1']
cube_beam.stats1.read_attrs = ['total']
cube_beam.read_attrs.append('stats2')
cube_beam.stats2.read_attrs = ['total']
cube_beam.read_attrs.append('stats3')
cube_beam.stats3.read_attrs = ['total']
cube_beam.read_attrs.append('stats4')
cube_beam.stats4.read_attrs = ['total']
cube_beam.read_attrs.append('stats5')
cube_beam.stats5.read_attrs = ['total']


dif_beam = StandardCam('XF:23ID1-ES{Dif-Cam:Beam}', name='dif_beam')
# fs1 = StandardCam('XF:23IDA-BI:1{FS:1-Cam:1}', name='fs1')

dif_beam.read_attrs = ['stats1']
dif_beam.stats1.read_attrs = ['total']
dif_beam.read_attrs.append('stats2')
dif_beam.stats2.read_attrs = ['total']
dif_beam.read_attrs.append('stats3')
dif_beam.stats3.read_attrs = ['total']
dif_beam.read_attrs.append('stats4')
dif_beam.stats4.read_attrs = ['total']
dif_beam.read_attrs.append('stats5')
dif_beam.stats5.read_attrs = ['total']



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

fccd = ProductionCamCustom('XF:23ID1-ES{FCCD}', name='fccd')
fccd.read_attrs = ['hdf5']
fccd.hdf5.read_attrs = []
fccd.configuration_attrs = ['cam.acquire_time',
                            'cam.acquire_period']
#                            'plugin_num_images']

## Adding useful info..
fccd.read_attrs.append('acquire_time')
# StandardCam does not have these; only Custom does. Add them
# to read_attrs only if they are present.
if 'num_images_captured' in fccd.signal_names:
    fccd.read_attrs.append('num_images_captured')
if 'plugin_num_images' in fccd.signal_names:
    fccd.read_attrs.append('plugin_num_images')

fccd.read_attrs.append('stats1')
fccd.stats1.read_attrs = ['total']
fccd.read_attrs.append('stats2')
fccd.stats2.read_attrs = ['total']
fccd.read_attrs.append('stats3')
fccd.stats3.read_attrs = ['total']
fccd.read_attrs.append('stats4')
fccd.stats4.read_attrs = ['total']
fccd.read_attrs.append('stats5')
fccd.stats5.read_attrs = ['total']


# CM commented on 2017_07_05 due to connection error preventing BSUI to
# start suitably..
#
## Test CCD
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
        self._pv_wfrm_n = epics.PV("{}Val:TimeN-I".format(pv_basename), auto_monitor=False)
        self._pv_wfrm = epics.PV("{}Val:Time-Wfrm".format(pv_basename), auto_monitor=False)
        self._pv_wfrm_nord = epics.PV("{}Val:Time-Wfrm.NORD".format(pv_basename), auto_monitor=False)
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
        self._pv_sel.put(2, wait=True) # Put us in reset mode
        self._pv_rst.put(1, wait=True) # Trigger processing
        self._pv_sel.put(1, wait=True) # Start Buffer
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

        for i,v in enumerate(payload):
           if self._data_is_time:
                x = v;
           else:
                x = i;
           ev = {'data': {self._name: x},
                  'timestamps': {self._name: v},
                 'time': v}
           yield ev

    def stop(self):
        self._pv_sel.put(0, wait=True) # Stop Collection

    def describe_collect(self):
        return {self._name: {self._name: {'source': self._pv_basename, 'dtype': 'number', 'shape': None}}}


topoff_inj = WaveformCollector('topoff_inj', 'XF:23ID1-SR{TO-Inj}', data_is_time=False)
topoff_btr = WaveformCollector('topoff_btr', 'XF:23ID1-SR{TO-BS}', data_is_time=False)
fccd_time = WaveformCollector('fccd_time', 'XF:23ID1-ES{FCCD-TS}')


class AreaDetectorTimeseriesCollector:
    def __init__(self, name, pv_basename, num_points = 1000000):
        self.root = self
        self.parent = None
        self._name = name
        self._pv_basename = pv_basename
        self._num_points = num_points

        self._pv_tscontrol = epics.PV("{}TSControl".format(pv_basename))
        self._pv_num_points = epics.PV("{}TSNumPoints".format(pv_basename))
        self._pv_cur_point = epics.PV("{}TSCurrentPoint".format(pv_basename))
        self._pv_wfrm = epics.PV("{}TSTotal".format(pv_basename), auto_monitor=False)
        self._pv_wfrm_ts = epics.PV("{}TSTimestamp".format(pv_basename), auto_monitor=False)
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
        #self._pv_num_points.put(self._num_points, wait=True)
        self._pv_tscontrol.put(0, wait=True) # Erase buffer and start collection
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
        for v,t in zip(payload_val, payload_time):
            ev = {'data': {self._name: v},
                  'timestamps': {self._name: t},
                  'time': ttime.time()}
            yield ev

    def stop(self):
        self._pv_tscontrol.put(2, wait=True) # Stop Collection

    def describe_collect(self):
        return {self._name: {self._name: {'source': self._pv_basename, 'dtype': 'number', 'shape': None}}}

diag6_flyer1 = AreaDetectorTimeseriesCollector('diag6_flyer1',
                                               'XF:23ID1-BI{Diag:6-Cam:1}Stats1:',
                                               num_points=100000000)
diag6_flyer5 = AreaDetectorTimeseriesCollector('diag6_flyer5',
                                               'XF:23ID1-BI{Diag:6-Cam:1}Stats5:',
                                               num_points=100000000)
fccd_flyer5 = AreaDetectorTimeseriesCollector('fccd_flyer5',
                                              'XF:23ID1-ES{FCCD}Stats5:',
                                              num_points=100000000)
fccd_flyer1 = AreaDetectorTimeseriesCollector('fccd_flyer1',
                                              'XF:23ID1-ES{FCCD}Stats1:',
                                              num_points=100000000)

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
#vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time']
vortex.read_attrs = ['mca.spectrum', 'mca.preset_live_time', 'mca.rois']
vortex.mca.read_attrs.append('rois')
vortex.mca.rois.read_attrs = ['roi0','roi1','roi2','roi3','roi4']
#gs.TABLE_COLS = ['vortex_mca_rois_roi4_count']; gs.PLOT_Y = 'vortex_mca_rois_roi4_count'


