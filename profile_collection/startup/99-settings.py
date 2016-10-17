#gs.COUNT_TIME = 1  # seconds

#
## These detectors will be read by the scans defined
## in 98-quick-scans.py, such as lup.
gs.DETS = [theta, delta, gamma,
           sx, say, saz, cryoangle,
           sy, sz,
           temp, uw_temp,
           pgm_en,
           epu1, epu2,
           slt1, slt2, slt3,
           m1a, m3a,
           mono_tempa, mono_tempb,  grt1_temp, grt2_temp]

## After the new implementation in Ophyd/Bluesky
theta.user_readback.name = 'theta'
delta.user_readback.name = 'delta'
gamma.user_readback.name = 'gamma'

pgm_en.readback.name = 'energy'

sclr.channels.read_attrs=['chan1','chan2','chan3','chan4','chan5','chan6']



#gs.MASTER_DET = sclr
#gs.MASTER_DET_FIELD = 'sclr_chan2'
#
## These are used by th2th
gs.TH_MOTOR = theta
gs.TTH_MOTOR = delta  # an approximation...
#
#gs.TABLE_COLS = ['sclr_chan4']
#gs.PLOT_Y = 'sclr_chan4'

gs.DETS.append(ring_curr)
gs.DETS.append(nanop)
#gs.DETS.append(sm_i)
#gs.DETS.append(sm_v)
#gs.DETS.append(sm_r)
#gs.DETS.append(npbx)
#gs.DETS.append(npby)
#gs.DETS.append(npbz)
#gs.DETS.append(nptx)
#gs.DETS.append(npty)
#gs.DETS.append(nptz)

gs.DETS.append(sclr)
gs.DETS.append(diag6_monitor)

gs.COUNT_TIME = 1

#gs.DETS.append(dif_beam_cam)
#gs.TABLE_COLS =['dif_beam_cam_stats_total3']
#gs.PLOT_Y='dif_beam_cam_stats_total3'

# for fCCD data saving

#gs.DETS.append(fccd)
#fccd.acquire_period = 1
#fccd.num_images = 5

#gs.TABLE_COLS = ['fccd_stats_total1']
#gs.PLOT_Y = 'fccd_stats_total1'


#ct.flyers = [topoff_inj, fccd_flyer5, diag6_flyer1]   # this only activiates flyers for ct()

#gs.FLYERS = [topoff_inj, fccd_flyer5, diag6_flyer1]   # this is for all scans on ophyd level

### New figure feature

def relabel_fig(fig, new_label):
    fig.set_label(new_label)
    fig.canvas.manager.set_window_title(fig.get_label())




import os
from datetime import datetime

def write_spec_header(path, doc):
    # write a new spec file header!
    #F /home/xf11id/specfiles/test.spec
    #E 1449179338.3418093
    #D 2015-12-03 16:48:58.341809
    #C xf11id  User = xf11id
    #O [list of all motors, 10 per line]
    session_manager = get_session_manager()
    pos = session_manager.get_positioners()
    spec_header = [
        '#F %s' % path,
        '#E %s' % int(doc['time']),
        # time might need to be formatted specifically
        '#D %s' % datetime.fromtimestamp(doc['time']),
        '#C %s  User = %s' % (doc['owner'], doc['owner']),
        'O0 {}'.format(' '.join(sorted(list(pos.keys()))))
    ]
    with open(path, 'w') as f:
        f.write('\n'.join(spec_header))
    return spec_header

class LiveSpecFile(CallbackBase):
    def start(self, doc):
        if not os.path.exists(gs.specpath):
            spec_header = write_spec_header(gs.specpath, doc)
        #else:
        #    spec_header = get_spec_header()
        last_command = list(
            get_ipython().history_manager.get_range())[-1][2]
        last_command = last_command.replace('(', ' ')
        last_command = last_command.replace(')', ' ')
        last_command = last_command.replace(',', ' ')
        self.acquisition_time = gs.COUNT_TIME
        # write a blank line between scans
        with open(gs.specpath, 'a') as f:
            f.write('\n\n')
        # write the new scan entry
        with open(gs.specpath, 'a') as f:
            f.write('#S %s %s\n' % (doc['scan_id'], last_command))
            f.write('#D %s\n' % datetime.fromtimestamp(doc['time']))
            f.write('#T %s (Seconds)\n' % self.acquisition_time)
        # write the motor positions
        session_manager = get_session_manager()
        pos = session_manager.get_positioners()
        positions = [str(v.position) for k, v in sorted(pos.items())]
        with open(gs.specpath, 'a') as f:
            f.write('#P0 {0}\n'.format(' '.join(positions)))
        # writing the list of motor names and their current values in
        # a more human readable way. Apparently "#M" is not a used key in
        # spec. Fingers crossed....
        with open(gs.specpath, 'a') as f:
            for idx, (name, positioner) in enumerate(sorted(pos.items())):
                f.write('#M%s %s %s\n' % (idx, name, str(positioner.position)))
        print("RunStart document received in LiveSpecFile")
        #raise
        self.motorname = last_command.split(' ')[1]

    def descriptor(self, doc):
        print('descriptor received')
        keys = sorted(list(doc['data_keys'].keys()))
        keys.remove(self.motorname)
        keys.insert(0, 'Seconds')
        keys.insert(0, 'Epoch')
        keys.insert(0, self.motorname)
        with open(gs.specpath, 'a') as f:
            f.write('#N %s\n' % len(keys))
            f.write('#L {0}    {1}\n'.format(keys[0],
                                             '  '.join(keys[1:])))

    def event(self, doc):
        print('event received')
        t = int(doc['time'])
        vals = [v for k, v in sorted(doc['data'].items()) if k != self.motorname]
        vals.insert(0, self.acquisition_time)
        vals.insert(0, t)
        vals.insert(0, doc['data'][self.motorname])
        vals = [str(v) for v in vals]
        with open(gs.specpath, 'a') as f:
            f.write('{0}  {1}\n'.format(vals[0], ' '.join(vals[1:])))

gs.specpath = os.path.expanduser('~/specfiles/test.spec')
live_specfile_callback = LiveSpecFile()
#gs.RE.subscribe('all', live_specfile_callback)
