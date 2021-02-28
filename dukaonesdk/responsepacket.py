"""Implements a class for the UDP data packet"""
from .mode import Mode
from .speed import Speed
from .dukapacket import DukaPacket


class ResponsePacket (DukaPacket):
    """A udp data packet from the duka device."""

    parameter_size = {
        0x01: 1,   # On off
        0x02: 1,   # Speed 1-3 255=manual
        0x06: 1,   # Boot mode
        0x07: 1,   # Timer mode
        0x0B: 3,   # Timer countdown
        0x0F: 1,   # Humidity sensor activation
        0x14: 1,   # Relay sensor activation
        0x16: 1,   # 0-10v sensor activation
        0x19: 1,   # Humidity threshold
        0x24: 2,   # Current RTC battery voltage 0-5000mv
        0x25: 1,   # Current humidity 0-100
        0x2D: 1,   # Current 0-10v sensor 0-100
        0x32: 1,   # Current relay sensor state
        0x44: 1,   # Manual speed
        0x4A: 2,   # Fan 1 speed 0-5000rpm
        0x4B: 2,   # Fan 2 speed 0-5000rpm
        0x64: 3,   # Filter timer byte 1=minutes, byte 2=hours, byte 3=days
        0x65: 1,   # Reset filter timer (1 byte data is ignored)
        0x66: 1,   # Boost mode deactivation delay 0-60 minutes
        0x6F: 3,   # RTC time
        0x70: 4,   # RTC calender
        0x72: 1,   # Weekly schedule
        0x77: 6,   # Schedule setup
        0x7C: 16,  # device search
        0x7D: 0,   # Device password
        0x7E: 4,   # MAchine hours
        0x80: 1,   # Reset alarms
        0x83: 1,   # Alarm indicator 0=no,1=Alarm, 2=warning
        0x85: 1,   # Cloud server operation permission
        0x86: 6,   # Firmware version and date
        0x87: 1,   # Restore factory settings
        0x88: 1,   # Filter replacement 0=ok, 1=replace
        0x94: 1,   # Wifi mode
        0x95: 0,   # Wifi name in client mode
        0x96: 0,   # Wifi password
        0x99: 1,   # Wifi encryption
        0x9A: 1,   # Wifi channel 1-13
        0x9B: 1,   # Wifi DHCP
        0x9C: 4,   # IP Address
        0x9D: 4,   # Subnet mask
        0x9E: 4,   # Gateway
        0xB7: 1,   # Ventilator mode 0=ventilation,1=heat recovery,2=supply
        0xB9: 2,   # Unit type
    }

    def __init__(self):
        super(ResponsePacket, self).__init__()
        self.device_id = None
        self.device_password = None
        self.is_on = None
        self.speed: Speed = None
        self.manualspeed = None
        self.fan1rpm = None
        self.humidity = None
        self.mode: Mode = None
        self.filter_alarm = None
        self.filter_timer = None
        self.search_device_id = None

    def initialize_from_data(self, data) -> bool:
        """Initialize a packet from data revieved from the device
        Returns False if the data is invalid
        """
        try:
            self._data = data
            size = len(data)
            if size < 4 or not self.is_header_ok():
                return False
            checksum = self.calc_checksum(size-2)
            datachecksum = self._data[size-2] + (self._data[size-1] << 8)
            if checksum != datachecksum:
                return False
            self.device_id = self.read_string()
            self.device_password = self.read_string()
            func = self.read_byte()
            if func != self.Func.RESPONSE.value:
                return False
            return self.read_parameters()
        except Exception:
            return False

    def is_header_ok(self):
        if self.read_byte() != 0xFD or self.read_byte() != 0xFD:
            return False
        return self.read_byte() == 0x02

    def read_byte(self) -> int:
        byte = self._data[self._pos]
        self._pos = self._pos+1
        return byte

    def read_string(self) -> str:
        strlen = self.read_byte()
        txt = ""
        for i in range(self._pos, self._pos+strlen):
            txt += chr(self._data[i])
        self._pos += strlen
        return txt

    def read_parameters(self) -> bool:
        while self._pos < len(self._data)-3:
            parameter = self.read_byte()
            size = 1
            if parameter == 0xFE:
                # change parameter size
                size = self.read_byte()
                parameter = self.read_byte()
            else:
                if parameter not in self.parameter_size:
                    return False
                size = self.parameter_size[parameter]
            if parameter == self.Parameters.ON_OFF.value:
                self.is_on = self._data[self._pos] != 0
            elif parameter == self.Parameters.SPEED.value:
                self.speed = self._data[self._pos]
            elif parameter == self.Parameters.MANUAL_SPEED.value:
                self.manualspeed = self._data[self._pos]
            elif parameter == self.Parameters.FAN1RPM.value:
                self.fan1rpm = (self._data[self._pos] +
                                (self._data[self._pos+1] << 8))
            elif parameter == self.Parameters.CURRENT_HUMIDITY.value:
                self.humidity = self._data[self._pos]
            elif parameter == self.Parameters.VENTILATION_MODE.value:
                self.mode = self._data[self._pos]
            elif parameter == self.Parameters.FILTER_ALARM.value:
                self.filter_alarm = self._data[self._pos]
            elif parameter == self.Parameters.FILTER_TIMER.value:
                self.filter_timer = self._data[self._pos] + \
                    (self._data[self._pos+2]*24 + self._data[self._pos+1])*60
            elif parameter == self.Parameters.SEARCH.value:
                self.search_device_id = ""
                for i in range(self._pos, self._pos+16):
                    self.search_device_id += chr(self._data[i])
            self._pos += size
        if self.is_on is not None and not self.is_on:
            self.speed = Speed.OFF

        return True
