import argparse

def non_negative_int (value):
    try:
        ivalue = int (value)
    except ValueError:
        # value does not represent an integer
        raise argparse.ArgumentTypeError (
            '{0} must be an integer >= 0'.format (value))

    if (ivalue < 0):
        # value represents an integer less than 0
        raise argparse.ArgumentTypeError (
            '{0} must be an integer >= 0'.format (value))

    return ivalue
