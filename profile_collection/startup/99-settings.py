# interactive use
sd.monitors = []  # a list of signals to monitor concurrently
sd.flyers = []  # a list of "flyable" devices
# a list of devices to read at start and end
sd.baseline = [theta, delta, gamma,
               sx, say, saz, cryoangle,
               sy, sz,
               temp, uw_temp,
               pgm_en,
               epu1, epu2,
               slt1, slt2, slt3,
               m1a, m3a,
               mono_tempa, mono_tempb,  grt1_temp, grt2_temp]

dets = [sclr]

pgm_en.readback.name = 'energy'

sclr.names.read_attrs=['name1','name2','name3','name4','name5','name6']  # WHAT IS THIS??? - Dan Allan
sclr.channels.read_attrs=['chan1','chan2','chan3','chan4','chan5','chan6']
sclr.hints = {'fields': ['sclr_ch2', 'sclr_ch3', 'sclr_ch6']}


# for fCCD data saving

#gs.DETS.append(fccd)
#fccd.acquire_period = 1
#fccd.num_images = 5


#sd.flyers = [topoff_inj, fccd_flyer5, diag6_flyer1]   # this is for all scans on ophyd level

### New figure feature

def relabel_fig(fig, new_label):
    fig.set_label(new_label)
    fig.canvas.manager.set_window_title(fig.get_label())


fccd.hints = {'fields': ['fccd_stats1_total']}
