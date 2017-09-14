import sys


def spin_progress_bar(val):
    """
    Spins the progress bar based on the modulo of val

    :param val: The value of the current progress
    """
    modulo = val % 4
    if modulo == 0:
        sys.stdout.write('\b/')
    elif modulo == 1:
        sys.stdout.write('\b-')
    elif modulo == 2:
        sys.stdout.write('\b\\')
    elif modulo == 3:
        sys.stdout.write('\b|')
    sys.stdout.flush()

