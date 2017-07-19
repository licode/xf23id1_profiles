from databroker_browser.qt import BrowserWindow, CrossSection, StackViewer


def search_result(h):
    if h.start.get('motors', None):
        return "{start[plan_name]} scanning {start[motors]} ['{start[uid]:.6}']".format(**h)
    else:
        return "{start[plan_name]} ['{start[uid]:.6}']".format(**h)

def text_summary(h):
    lines = []
    if 'sample' in h['start']:
        lines.append('Sample: {}'.format(h['start']['sample']))
    return '\n'.join(lines)


def fig_dispatch(header, factory):
    plan_name = header['start']['plan_name']
    if 'image_det' in header['start']['detectors']:
        fig = factory('Image Series')
        cs = CrossSection(fig)
        sv = StackViewer(cs, db.get_images(header, 'image'))
    elif len(header['start'].get('motors', [])) == 1:
        motor, = header['start']['motors']
        #main_det, *_ = header['start']['detectors']  #AB commented out. DA originted.  THis plots theta with Yaxis
        main_det =  header.table().fccd_stats2_total  #AB added FCCD as maindet
        fig = factory("{} vs {}".format(main_det, motor))
        ax = fig.gca()
        lp = LivePlot(gs.PLOT_Ymain_det, motor, ax=ax)
        db.process(header, lp)


def browse():
    # Use databroker filters feature to limit results to, say, a
    # particular user group.
    # db.add_filter(saf_num='...')
    return BrowserWindow(db, fig_dispatch, text_summary, search_result)
