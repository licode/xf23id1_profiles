from epics import caget, caput
import time


def shclose():
    #caput('XF:23ID1-VA{Diag:06-GV:1}Cmd:Cls-Cmd', 1, wait=True)  # wears our valve. don't use
    #caput('XF:23ID1-PPS{PSh}Cmd:Cls-Cmd', 1, wait=True) 	  # use if DP:1-Sh:1 is broken
    caput('XF:23IDA-EPS{DP:1-Sh:1}Cmd:In-Cmd',1)
    #time.sleep(1)
    while shchk():
        #raise Exception('Inconsistent shutter status!')
        time.sleep(0.5)


def shopen():
    #caput('XF:23ID1-VA{Diag:06-GV:1}Cmd:Opn-Cmd', 1, wait=True)
    #caput('XF:23ID1-PPS{PSh}Cmd:Opn-Cmd', 1, wait=True)
    caput('XF:23IDA-EPS{DP:1-Sh:1}Cmd:Out-Cmd',1)
    #time.sleep(1)
    while not shchk():
        #raise Exception('Inconsistent shutter status!')
        time.sleep(0.5)


def shchk():
    #shutter_open = caget('XF:23ID1-VA{Diag:06-GV:1}Pos-Sts')
    #shutter_open = 1 - caget('XF:23ID1-PPS{PSh}Pos-Sts')
     return  caget('XF:23IDA-EPS{DP:1-Sh:1}Pos-Sts') == 0


def save_new_bg():
    # Record initial shutter status
    shutter_open = shchk()

    # Close Shutter
    shclose()

    # Disable Background
    caput('XF:23ID1-ES{FCCD}Proc1:EnableBackground', 0)

    # Disable Filter
    caput('XF:23ID1-ES{FCCD}Proc1:EnableFilter', 0)

    # Get FCCD count time and wait for 3 x count time
    count_time = caget('XF:23ID1-ES{FCCD}cam1:AcquireTime')
    time.sleep(count_time*2+2)

    # Re-take background
    #caput('XF:23ID1-ES{FCCD}Proc1:SaveBackground', 0)
    caput('XF:23ID1-ES{FCCD}Proc1:SaveBackground', 1)

    # Enable Background
    caput('XF:23ID1-ES{FCCD}Proc1:EnableBackground', 1)

    # Open shutter again if it was initially open
    if shutter_open:
        shopen()
        time.sleep(0.5)


def _ct_dark():
    caput('XF:23ID1-ES{LED:1}Sw-Cmd',0)
    caput('XF:23ID1-ES{LED:2}Sw-Cmd',0)
    #ct(dark_field = True, camera_config = {'camera_freq': fccd.frequency, 'camera_gain': caget('XF:23ID1-ES{FCCD}cam1:FCRICGain'), 'camera_frames': fccd.num_images, 'chip_temp': caget('XF:23ID1-ES{TCtrl:2-Chan:A}T:C-I')})
    ct()


def ct_dark():
    shutter_open = shchk()

    # Close shutter
    shclose()
    time.sleep(0.5)

    print('\nShutter closed. Collecting dark images.')
    _ct_dark()

    # Open shutter again if it was initially open
    if shutter_open:
        shopen()
        time.sleep(0.5)
        print('\nShutter opened.')


def ct_all_dark():

    print('\nStarting procedure to acquire camera gains at {}Hz'.format(1/fccd.acquire_time))
    # Save current settings
    shutter_open = shchk()
    initial_gain = caget('XF:23ID1-ES{FCCD}cam1:FCRICGain')

    # Close shutter
    shclose()

    for gain_bit in [2, 1, 0]: # corresponds to camera gain of [1, 2, 8] respectively
        caput('XF:23ID1-ES{FCCD}cam1:CameraPwr',0)
        time.sleep(2)
        caput('XF:23ID1-ES{FCCD}cam1:Acquire', 0)
        print('\nCamera stopped..')
        time.sleep(2)
        caput('XF:23ID1-ES{FCCD}cam1:FCRICGain', gain_bit)#, wait=False)
        print('\nGain bit set to {}'.format(gain_bit))
        time.sleep(3)
        caput('XF:23ID1-ES{FCCD}cam1:Acquire', 1)
        time.sleep(2)
        caput('XF:23ID1-ES{FCCD}cam1:CameraPwr',1)
        print('\nCamera restarted..')
        time.sleep(2)
        _ct_dark()

    # Restore initial gain setting
    caput('XF:23ID1-ES{FCCD}cam1:FCRICGain', initial_gain)#, wait=False)
    time.sleep(3)
    print('\nReturned to initial gain setting and restarting acquisition')

    # Restart camera acquisition
    caput('XF:23ID1-ES{FCCD}cam1:Acquire', 1)#, wait=False)

    # Open shutter again if it was initially open
    if shutter_open:
        shopen()
        time.sleep(0.5)


def del_det(det):
    if det in gs.DETS:
        gs.DETS.remove(det)
    else:
        print('Detector not in gs.DETS')

    if det == sclr:
        gs.TABLE_COLS = ['fccd_stats_total1']
        gs.PLOT_Y = 'fccd_stats_total1'
    elif det == fccd:
        gs.TABLE_COLS = ['sclr_chan2']
        gs.PLOT_Y = 'sclr_chan2'


def set_det(det):
    if det not in gs.DETS:
        gs.DETS.append(det)

    if det == dif_beam_cam:
        if fccd in gs.DETS:
            gs.DETS.remove(fccd)
        gs.TABLE_COLS = ['dif_beam_cam_stats_total1', 'dif_beam_cam_stats_total3']
        gs.PLOT_Y = 'dif_beam_cam_stats_total3'
    if det == sclr:
        if fccd in gs.DETS:
            gs.DETS.remove(fccd)
        gs.TABLE_COLS = ['sclr_chan2']
        gs.PLOT_Y = 'sclr_chan2'
    elif det == fccd:
        #if sclr in gs.DETS:
            #gs.DETS.remove(sclr)
        gs.TABLE_COLS = ['fccd_stats_total1']
        gs.PLOT_Y = 'fccd_stats_total1'


def add_det(det):
    if det not in gs.DETS:
        gs.DETS.append(det)

    if det == sclr:
        if 'sclr_chan2' not in gs.TABLE_COLS:
            gs.TABLE_COLS.append('sclr_chan2')
        gs.PLOT_Y = 'sclr_chan2'
    elif det == fccd:
        if 'fccd_stats_total1' not in gs.TABLE_COLS:
            gs.TABLE_COLS.append('fccd_stats_total1')
        gs.PLOT_Y = 'fccd_stats_total1'

def ct_fccd(freq, num_images):
    fccd.frequency = freq
    fccd.acquire_time = 1/fccd.frequency
    fccd.num_images = num_images
    sleep(1)
    gs.COUNT_TIME = fccd.num_images * fccd.acquire_time
    ct()


import itertools

def exp_decay(tc, t0=1):
   c = itertools.count()
   for i in c:
       yield t0 * np.exp(-i/tc)
