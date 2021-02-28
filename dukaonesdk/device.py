"""Implements the duka one device class """
from .mode import Mode
from .speed import Speed


class Device:
    """A class representing a single Duke One Device """

    def __init__(self, deviceid: str, password: str = None,
                 ip_address: str = "<broadcast>", onchange=None):
        self._id = deviceid
        self._password = password
        self._ip_address = ip_address
        self._speed: Speed = None
        self._mode: Mode = None
        self._manualspeed: int = None
        self._fan1rpm: int = None
        self._humidity: int = None
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
        return self._ip_address

    @property
    def speed(self) -> Speed:
        """Return the speed of the device"""
        return self._speed

    @property
    def manualspeed(self) -> int:
        """Return the manual speed of the device"""
        return self._manualspeed

    @property
    def fan1rpm(self) -> int:
        """Return the fan1 rpm of the device"""
        return self._fan1rpm

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

    @property
    def humidity(self) -> int:
        return self._humidity
