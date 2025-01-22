import time


def getUptime(
    start_time: time,
) -> time:
    """
    Returns the number of seconds since the program started.
    """
    return time.time() - start_time
    