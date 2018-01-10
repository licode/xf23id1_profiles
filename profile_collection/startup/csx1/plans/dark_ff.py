# dark and flatfield plans

import bluesky.plans as bp
from ..startup.optics import inout
from ..startup.detectors import fccd


def ct_dark(numim=None,detectors=[fccd], gain_std=0):
    """Collect dark images for fccd and add metadata tag for dark and gain. The pre-count shutter & gain states preserved.

    Parameters
    -----------
    numim: int
        Number of images to be measured. If different from current setting, the number of images will revert back to the original after the scan is complete.

    detectors: list
        List of detectors to be recorded.
        Default = [fccd]

    gain_std: int
        List of detectors to be recorded.
        Default = 0   (which is 'Auto' or x8, the most sensitive gain)

    Returns
    -----------
    """
    try:
        #TODO figureout kwargs and self to mkae up to line 44 a single definition
        oldnumim = fccd.cam.num_images.value

        #Printing info
        print('\nStarting procedure to acquire darks {:3.3}Hz or {:3.3f}s.\n'.format(1/fccd.cam.acquire_time.value,fccd.cam.acquire_time.value))
        print('\tCurrent number of images = {}.\n'.format(fccd.cam.num_images.value))

        yield from bp.sleep(.3)

        if numim != None:
            print('\tSetting to {} images.\n'.format(numim))
            yield from abs_set(fccd.cam.num_images,numim,wait=True)

        dark_shutter_state = inout.status.value
        dark_sh_dict ={'Inserted':'In', 'Not Inserted':'Out'}
        gain_state = fccd.cam.fcric_gain.value
        gain_bit_dict = {0:'auto',1:'x2',2:'x1'}

        yield from bp.mv(inout,'In')
        yield from bp.sleep(fccd.cam.acquire_period.value*2.01) # This has to be 2 until we can selectively remove dark images get_fastccd_images()
        yield from bp.mv(fccd.fccd1.capture_bgnd,1)  # SET TO 1 TO ARM FOR NEXT EVENT so that the FastCCD1 is already bkg subt

        #take darks
        yield from _ct_dark(detectors,gain_std,gain_bit_dict)

        #Putting things back
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)

    except Exception:
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)
        raise
    except KeyboardInterrupt:
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)
        raise



def _ct_dark(detectors,gain_bit_input, gain_bit_dict):
    yield from bp.mv(fccd.cam.fcric_gain, gain_bit_input)
    #if _gain_bit_input != 0:
    #    yield from bp.sleep(fccd.cam.acquire_period.value*2.01) # This has to be 2 until we can selectively remove dark images get_fastccd_images()
    print('\n\nGain bit set to {} for a gain value of {}\n'.format(gain_bit_input,gain_bit_dict.get(gain_bit_input)))

    #TODO use md csxtools dark correction
    yield from count(detectors, md={'fccd': {'image':'dark', 'gain': gain_bit_dict.get(gain_bit_input)}})

    ## Commented this out because we should be using the md
    #olog('ScanNo {} Darks at for {}Hz or {}s with most sensitive gain ({},Auto)'.format(db[-1].start['scan_id'],1/fccd.cam.acquire_time.value,fccd.cam.acquire_time.value,fccd.cam.fcric_gain.value))

def _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict,dark_shutter_state):
    print('\nReturning to intial conditions (pre-count).')
    yield from abs_set(fccd.cam.num_images,oldnumim,wait=True)

    yield from bp.mv(fccd.cam.fcric_gain, gain_state)
    yield from bp.mv(inout,dark_sh_dict.get(dark_shutter_state))
    yield from bp.sleep(fccd.cam.acquire_period.value)

    print('\tTotal images per trigger are NOW:\t {}'.format(fccd.cam.num_images.setpoint))
    print('\tFCCD FCRIC gain value is NOW:\t\t {}\n\n'.format(gain_bit_dict.get(fccd.cam.fcric_gain.value)))


def ct_dark_all(numim=None,detectors=[fccd]):
    """Collect dark images for fccd and add metadata tag for dark and gain. The pre-count shutter & gain states preserved.

    Parameters
    -----------
    numim: int
        Number of images to be measured.

    detectors: list
        List of detectors to be recorded.
        Default = [fccd]

    Returns
    -----------
    """
    try:
        oldnumim = fccd.cam.num_images.value

        #Printing info
        print('\nStarting procedure to acquire darks {:3.3}Hz or {:3.3f}s.\n'.format(1/fccd.cam.acquire_time.value,fccd.cam.acquire_time.value))
        print('\tCurrent number of images = {}.\n'.format(fccd.cam.num_images.value))

        yield from bp.sleep(.3)

        if numim != None:
            print('\tSetting to {} images.\n'.format(numim))
            yield from abs_set(fccd.cam.num_images,numim,wait=True)

        dark_shutter_state = inout.status.value
        dark_sh_dict ={'Inserted':'In', 'Not Inserted':'Out'}
        gain_state = fccd.cam.fcric_gain.value

        gain_bit_dict = {0:'auto',1:'x2',2:'x1'}

        yield from bp.mv(inout,'In')
        yield from bp.sleep(fccd.cam.acquire_period.value*2.01) # This has to be 2 until we can selectively remove dark images get_fastccd_images()
        yield from bp.mv(fccd.fccd1.capture_bgnd,1)  # SET TO 1 TO ARM FOR NEXT EVENT so that the FastCCD1 is already bkg subt

        #take darks
        for i in range(0,3):
            gain_std = i
            yield from _ct_dark(detectors,gain_std,gain_bit_dict)

        #Putting things back
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)

    except Exception:
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)
        raise
    except KeyboardInterrupt:
        yield from _ct_dark_cleanup(oldnumim,gain_bit_dict,gain_state,dark_sh_dict, dark_shutter_state)
        raise


