from enum import IntEnum

class Mode(IntEnum):
    """Device modes available
    Note: The ONEWAY derection is decided by the dip switch on the device
    """
    ONEWAY = 0
    TWOWAY = 1
    IN = 2
