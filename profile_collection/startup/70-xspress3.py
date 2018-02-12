from nslsii.detectors.xspress3 import (XspressTrigger,
                                         Xspress3Detector,
                                         Xspress3FileStore,
                                         Xspress3Channel)
from ophyd.areadetector.plugins import PluginBase

class CSXXspress3Detector(XspressTrigger, Xspress3Detector):
    roi_data = Cpt(PluginBase, 'ROIDATA:')
    channel1 = Cpt(Xspress3Channel,
                   'C1_', channel_num=1,
                   read_attrs=['rois'])

    hdf5 = Cpt(Xspress3FileStore, 'HDF5:',
               write_path_template='/GPFS/xf23id/xf23id1/xspress3_data/%Y/%m/%d/',
               root='/GPFS/xf23id/xf23id1/',
               fs=db.event_sources[0].fs)

    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,
                 **kwargs):
        if configuration_attrs is None:
            configuration_attrs = ['external_trig', 'total_points',
                                   'spectra_per_point', 'settings',
                                   'rewindable']
        if read_attrs is None:
            read_attrs = ['channel1', 'hdf5']
        super().__init__(prefix, configuration_attrs=configuration_attrs,
                         read_attrs=read_attrs, **kwargs)



xsp3 = CSXXspress3Detector('XF:23ID1-ES{XP3}:', name='xsp3')
for j, r in enumerate(xsp3.channel1.all_rois):
    r.value.name = 'xsp3_roi_{:02d}'.format(j+1)
    r.value_sum.name = 'xsp3_accumulated_roi_{:02d}'.format(j+1)
    r.read_attrs = ['value']

def setup_rois(channel, roi_width):
    for j, roi in enumerate(channel.all_rois):
        yield from bp.mv(roi.bin_low, j*roi_width)
        yield from bp.sleep(1)
        yield from bp.mv(roi.bin_high, (j+1)*roi_width)
        yield from bp.sleep(1)

def roi_for_elements(channel, list_of_elm):
    for roi, elm in zip(channel.all_rois, list_of_elm):
        low, high = get_range(elm)
        yield from bp.abs_set(roi.bin_low, low, wait=True, timeout=1)
        yield from bp.sleep(.5)
        yield from bp.abs_set(roi.bin_high, high, wait=True, timeout=1)
        yield from bp.sleep(.5)

def get_range(elm):
    elm_map = {'Fe': [70, 72],
               'Ni': [84, 86]}
    return elm_map[elm]

def monitor_mca_for_fccd(plan):
    monitored = False
    monitor_targets = [r.value for r in xsp3.channel1.all_rois]
    monitor_msgs = [Msg('monitor', s) for s in monitor_targets]
    unmonitor_msgs = [Msg('unmonitor', s) for s in monitor_targets]

    def watch_for_fccd_trigger(msg):
        if msg.command == 'trigger' and msg.obj is fccd:
            def new_gen():
                nonlocal monitored
                if not monitored:
                    monitored = True
                    # cheating
                    config = fccd.read_configuration()
                    total_time = config['fccd_cam_acquire_time']['value'] * config['fccd_plugin_num_images']['value']
                    exp_time = 1
                    xsp3.stage_sigs['settings.acquire_time'] = exp_time
                    xsp3.stage_sigs['settings.num_exposures'] =  int(total_time / exp_time) + 2
                    yield from bp.stage(xsp3)
                    yield from ensure_generator(monitor_msgs)

                yield from bp.trigger(xsp3)
                return (yield msg)

            return new_gen(), None
        elif msg.command == 'close_run':
            def stop_gen():
                yield from maybe_shutdown()
                return (yield msg)
            return stop_gen(), None


        else:
            return None, None

    def maybe_shutdown():
        nonlocal monitored
        if not monitored:
            return
        yield from ensure_generator(unmonitor_msgs)
        yield from bp.unstage(xsp3)
        monitored = False

    return (yield from finalize_wrapper(
        plan_mutator(plan, watch_for_fccd_trigger),
        maybe_shutdown()))