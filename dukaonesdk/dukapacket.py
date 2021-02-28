"""Implements a class for the UDP data packet"""
from enum import Enum
from .device import Device
from .mode import Mode
from .speed import Speed


class DukaPacket:
    """A udp data packet to/from the duka device."""
    class Func(Enum):
        READ = 1
        WRITE = 2
        WRITEREAD = 3
        INCREAD = 4
        DECREAD = 5
        RESPONSE = 6

    class Parameters(Enum):
        ON_OFF = 0x01
        SPEED = 0x02
        CURRENT_HUMIDITY = 0x25
        MANUAL_SPEED = 0x44
        FAN1RPM = 0x4A
        FILTER_TIMER = 0x64
        RESET_FILTER_TIMER = 0x65
        SEARCH = 0x7C
        RESET_ALARMS = 0x80
        READ_ALARM = 0x83
        FILTER_ALARM = 0x88
        VENTILATION_MODE = 0xB7

    def __init__(self):
        self._data = None
        self._pos = 0
        self.maxsize = 200

    def initialize_search_cmd(self):
        """Initialize a search command packet"""
        self.__build_data("DEFAULT_DEVICEID", "")
        self.__add_byte(DukaPacket.Func.READ.value)
        self.__add_byte(DukaPacket.Parameters.SEARCH.value)
        self.__add_checksum()

    def initialize_speed_cmd(self, device: Device, speed: Speed):
        """Initialize a speed command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(DukaPacket.Func.WRITEREAD.value)
        self.__add_byte(DukaPacket.Parameters.SPEED.value)
        self.__add_byte(speed)
        self.__add_checksum()

    def initialize_manualspeed_cmd(self, device: Device, manualspeed: int):
        """Initialize a manual speed command packet to be sent to a device
        The manuals speed is in the interval 0-255
        """
        self.__build_data(device.device_id, device.password)
        self.__add_byte(DukaPacket.Func.WRITEREAD.value)
        self.__add_byte(DukaPacket.Parameters.MANUAL_SPEED.value)
        self.__add_byte(manualspeed)
        self.__add_checksum()

    def initialize_mode_cmd(self, device: Device, mode: Mode):
        """Intialize a mode command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(DukaPacket.Func.WRITEREAD.value)
        self.__add_byte(DukaPacket.Parameters.VENTILATION_MODE.value)
        self.__add_byte(mode)
        self.__add_checksum()

    def initialize_on_cmd(self, device: Device):
        """Initialize a ON command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(DukaPacket.Func.WRITEREAD.value)
        self.__add_byte(DukaPacket.Parameters.ON_OFF.value)
        self.__add_byte(0x01)
        self.__add_checksum()

    def initialize_off_cmd(self, device: Device):
        """Initialize a Off command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(DukaPacket.Func.WRITEREAD.value)
        self.__add_byte(DukaPacket.Parameters.ON_OFF.value)
        self.__add_byte(0x00)
        self.__add_checksum()

    def initialize_status_cmd(self, device: Device):
        """Initialize a status command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(self.Func.READ.value)
        self.__add_byte(self.Parameters.ON_OFF.value)
        self.__add_byte(self.Parameters.VENTILATION_MODE.value)
        self.__add_byte(self.Parameters.SPEED.value)
        self.__add_byte(self.Parameters.MANUAL_SPEED.value)
        self.__add_byte(self.Parameters.FAN1RPM.value)
        self.__add_byte(self.Parameters.FILTER_ALARM.value)
        self.__add_byte(self.Parameters.FILTER_TIMER.value)
        self.__add_byte(self.Parameters.CURRENT_HUMIDITY.value)
        self.__add_checksum()

    def initialize_reset_filter_alarm_cmd(self, device: Device):
        """Initialize a reset filter alarm command packet to be sent to a
         device"""
        self.__build_data(device.device_id, device.password)
        self.__add_byte(self.Func.WRITE.value)
        self.__add_byte(self.Parameters.RESET_FILTER_TIMER.value)
        self.__add_checksum()

    @property
    def data(self):
        """Return the data for the packet"""
        return self._data[0:self._pos]

    def __add_byte(self, byte: int):
        """Add a byte to the packet"""
        self._data[self._pos] = byte
        self._pos += 1

    def __build_data(self, device_id: str, password: str):
        """Build a packet of the specified size"""
        self._data = bytearray(self.maxsize)
        self._pos = 0
        self.__add_byte(0xfd)
        self.__add_byte(0xfd)
        self.__add_byte(0x02)
        self.__add_byte(len(device_id))
        for char in device_id:
            self.__add_byte(ord(char))
        self.__add_byte(len(password))
        for char in password:
            self.__add_byte(ord(char))

    def __add_parameter(self, parameter: int, value):
        self.__add_byte(parameter)
        self.__add_byte(value)

    def __add_checksum(self):
        """Add a checksum to the packet"""
        checksum = self.calc_checksum(self._pos)
        self.__add_byte(checksum & 0xff)
        self.__add_byte(checksum >> 8)

    def calc_checksum(self, size) -> int:
        """Calculate the check sum for the packet"""
        checksum: int = 0
        for i in range(2, size):
            checksum += self._data[i]
        return checksum & 0xffff
