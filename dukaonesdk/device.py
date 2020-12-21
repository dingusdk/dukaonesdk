"""Implements the duka one device class """
from enum import IntEnum


class Speed(IntEnum):
    """Device speed options available """
    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MANUAL = 255


class Mode(IntEnum):
    """Device modes available
    Note: The ONEWAY derection is decided by the dip switch on the device
    """
    ONEWAY = 0
    TWOWAY = 1
    IN = 2


class Device:
    """A class representing a single Duke One Device """

    def __init__(self, deviceid: str, password: str = None,
                 ip_address: str = "<broadcast>", onchange=None):
        self._id = deviceid
        self._password = password
        self._ip = ip_address
        self._speed: Speed = None
        self._mode: Mode = None
        self._manualspeed: int = None
        self._filter_alarm = False
        self._filter_timer = None
        self._changeevent = onchange

    @property
    def device_id(self) -> str:
        """Return  the device id """
        return self._id

    @property
    def password(self) -> str:
        """Return the password for the device"""
        if self._password:
            return self._password
        return "1111"

    @property
    def ip_address(self) -> str:
        """Return the IP of the device"""
        return self._ip

    @property
    def speed(self) -> Speed:
        """Return the speed of the device"""
        return self._speed

    @property
    def manualspeed(self) -> int:
        """Return the manual speed of the device"""
        return self._manualspeed

    @property
    def mode(self) -> Mode:
        """Return the mode of the device"""
        return self._mode

    @property
    def filter_alarm(self) -> bool:
        """Return the filter alarm of the device"""
        return self._filter_alarm

    @property
    def filter_timer(self) -> int:
        return self._filter_timer

    def update(self, ip_address: str, speed: Speed, manualspeed: int,
               mode: Mode, filter_alarm: bool, filter_timer: int):
        """Update the device with data recieved. Called by the dukaclient"""
        haschange = False
        if ip_address is not None and ip_address != self._ip:
            self._ip = ip_address
            haschange = True
        if speed is not None and speed != self._speed:
            self._speed = speed
            haschange = True
        if manualspeed is not None and manualspeed != self._manualspeed:
            self._manualspeed = manualspeed
            haschange = True
        if mode is not None and mode != self._mode:
            self._mode = mode
            haschange = True
        if filter_alarm is not None and filter_alarm != self._filter_alarm:
            self._filter_alarm = filter_alarm
            haschange = True
        if filter_timer is not None and filter_timer != self._filter_timer:
            self._filter_timer = filter_timer
            haschange = True
        if haschange and self._changeevent is not None:
            self._changeevent(self)
