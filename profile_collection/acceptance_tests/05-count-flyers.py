from bluesky.plans import Count

ct = Count([])
ct.flyers = [topoff_inj, diag6_flyer5, diag6_flyer1]


uid, = RE(ct, LiveTable([]))
assert len(db[uid].descriptors) == 3  # one event stream per flyer
