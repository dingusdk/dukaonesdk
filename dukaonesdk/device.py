"""Implements the duka one device class """
import time
from .mode import Mode
from .speed import Speed


class Device:
    """A class representing a single Duke One Device"""

    def __init__(
        self,
        deviceid: str,
        password: str = None,
        ip_address: str = "<broadcast>",
        onchange=None,
    ):
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
        self._firmware_version = None
        self._firmware_date = None
        self._unit_type = None

    @property
    def device_id(self) -> str:
        """Return  the device id"""
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
        """Return the filter timer in minutes"""
        return self._filter_timer

    @property
    def humidity(self) -> int:
        """Return the humidity."""
        return self._humidity

    @property
    def firmware_version(self) -> str:
        """Return the firmware version of the duka one device"""
        return self._firmware_version

    @property
    def firmware_date(self) -> str:
        """return the firmware date"""
        return self._firmware_date

    @property
    def unit_type(self) -> int:
        return self._unit_type

    def is_initialized(self):
        """Returns True if the device has initilized.

        The device is initialize once the get initial get firmware packet has been received.
        This packet is send when the device is added to the client
        """
        return self.firmware_version is not None

    def wait_for_initialize(self):
        timeout = time.time() + 2
        while self.firmware_version is None and time.time() < timeout:
            time.sleep(0.1)
