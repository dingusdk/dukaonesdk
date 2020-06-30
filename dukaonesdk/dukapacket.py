"""Implements a class for the UDP data packet"""
from .device import Device, Mode, Speed


class DukaPacket:
    """A udp data packet to/from the duka device."""

    def __init__(self):
        self._data = None
        self._pos = 0
        self._datastart = 0

    def initialize_from_data(self, data) -> bool:
        """Initialize a packet from data revieved from the device"""
        self._data = data
        size = len(self._data)
        if size < 4:
            return False
        idlen = data[3]
        pswstart = 4 + idlen
        if size <= pswstart:
            return False
        pswlen = data[pswstart]
        self._datastart = pswstart+1+pswlen
        if size <= self._datastart:
            return False
        checksum = self.__calc_checksum()
        datachecksum = self._data[size-2] + (self._data[size-1] << 8)
        return checksum == datachecksum

    def initialize_speed_cmd(self, device: Device, speed: Speed):
        """Initialize a speed command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password, 8)
        self.__add_byte(0x03)
        self.__add_byte(0x02)
        self.__add_byte(speed)
        self.__add_byte(0xfc)
        self.__add_byte(0x01)
        self.__add_byte(0x07)
        self.__add_byte(0x0b)
        self.__add_byte(0x72)
        self.__add_checksum()

    def initialize_mode_cmd(self, device: Device, mode: Mode):
        """Intialize a mode command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password, 3)
        self.__add_byte(0x03)
        self.__add_byte(0xb7)
        self.__add_byte(mode)
        self.__add_checksum()

    def initialize_on_cmd(self, device: Device):
        """Initialize a ON command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password, 3)
        self.__add_byte(0x03)
        self.__add_byte(0x01)
        self.__add_byte(0x01)
        self.__add_checksum()

    def initialize_off_cmd(self, device: Device):
        """Initialize a Off command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password, 10)
        self.__add_byte(0x03)
        self.__add_byte(0x01)
        self.__add_byte(0x00)
        self.__add_byte(0xfc)
        self.__add_byte(0x01)
        self.__add_byte(0x07)
        self.__add_byte(0x0b)
        self.__add_byte(0x06)
        self.__add_byte(0x83)
        self.__add_byte(0x72)
        self.__add_checksum()

    def initialize_status_cmd(self, device: Device):
        """Initialize a status command packet to be sent to a device"""
        self.__build_data(device.device_id, device.password, 17)
        self.__add_byte(0x01)
        self.__add_byte(0xb9)
        self.__add_byte(0x01)
        self.__add_byte(0x02)
        self.__add_byte(0x44)
        self.__add_byte(0xb7)
        self.__add_byte(0x72)
        self.__add_byte(0x07)
        self.__add_byte(0x0b)
        self.__add_byte(0x06)
        self.__add_byte(0x88)
        self.__add_byte(0x83)
        self.__add_byte(0x32)
        self.__add_byte(0xff)
        self.__add_byte(0x03)
        self.__add_byte(0x04)
        self.__add_byte(0x05)
        self.__add_checksum()

    @property
    def data(self):
        """Return the data for the packet"""
        return self._data

    def is_response_from_device(self) -> bool:
        """Return true of the packet is from a device"""
        responsetype = self._data[self._datastart]
        return responsetype == 0x06

    def response_device_id(self) -> str:
        """Return the device id from the packet"""
        idlen = self._data[3]
        device_id = ""
        for i in range(4, 4+idlen):
            device_id += chr(self._data[i])
        return device_id

    def response_is_on(self) -> bool:
        """Return true if this is a response On packet"""
        on_packet = None
        if self._data[self._datastart+1] == 0xfe:
            on_packet = self._data[self._datastart + 7] == 0x01
        if self._data[self._datastart+1] == 0x02:
            return True
        return on_packet

    def response_speed(self) -> Speed:
        """Return the speed from the packet"""
        speed = None
        if self._data[self._datastart+1] == 0xfe:
            speed = self._data[self._datastart + 9]
        if self._data[self._datastart+1] == 0x02:
            speed = self._data[self._datastart + 2]
        return speed

    def response_mode(self) -> Mode:
        """Return the mode from the packet"""
        mode = None
        if self._data[self._datastart+1] == 0xfe:
            mode = self._data[self._datastart + 13]
        if self._data[self._datastart+1] == 0xb7:
            mode = self._data[self._datastart + 2]
        return mode

    def __add_byte(self, byte: int):
        """Add a byte to the packet"""
        self._data[self._pos] = byte
        self._pos += 1

    def __build_data(self, device_id: str, password: str, size: int):
        """Build a packet of the specified size"""
        totalsize = 5+len(device_id)+len(password)+size+2
        self._data = bytearray(totalsize)
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
        self._datastart = self._pos

    def __add_checksum(self):
        """Add a checksum to the packet"""
        checksum = self. __calc_checksum()
        self.__add_byte(checksum & 0xff)
        self.__add_byte(checksum >> 8)

    def __calc_checksum(self) -> int:
        """Calculate the check sum for the packet"""
        checksum: int = 0
        for i in range(2, len(self._data)-2):
            checksum += self._data[i]
        return checksum & 0xffff
