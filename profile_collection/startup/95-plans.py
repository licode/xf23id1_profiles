from collections import deque
import bluesky.plans as bp

@bp.planify
def fccd_aware_trigger_and_read(devices, name='primary'):
    """
    Variant of `bluesky.plans.triger_and_read` customized for CSX

    Normal behavior is to trigger, wait for triggering to finish, and then
    read. For SLOW_DEVICES, defined in the body of this function,
    this plan triggers, reads, and *then* waits for triggering to finish.

    Trigger and read a list of detectors and bundle readings into one Event.

    Parameters
    ----------
    devices : iterable
        devices to trigger (if they have a trigger method) and then read
    name : string, optional
        event stream name, a convenient human-friendly identifier; default
        name is 'primary'

    Yields
    ------
    msg : Msg
        messages to 'trigger', 'wait' and 'read'
    """
    SLOW_DEVICES = ['fccd']
    slow_device_seen = False
    devices = bp.separate_devices(devices)  # remove redundant entries
    normal_grp = bp._short_uid('trigger')
    slow_grp = bp._short_uid('slow-trigger')
    plan_stack = deque()
    for obj in devices:
        if obj.name in SLOW_DEVICES:
            slow_device_seen = True
            grp = slow_grp
        else:
            grp = normal_grp
        if hasattr(obj, 'trigger'):
            plan_stack.append(trigger(obj, group=grp))
    if plan_stack:
        plan_stack.append(bp.wait(group=normal_grp))
    with event_context(plan_stack, name=name):
        for obj in devices:
            plan_stack.append(bp.read(obj))
    if plan_stack and slow_device_seen:
        plan_stack.append(bp.wait(group=slow_grp))
    return plan_stack


# If this customization of triggering behavior causes unforeseen
# trouble, just comment out the following line. The definition
# above can stay.
#bp.trigger_and_read = fccd_aware_trigger_and_read
