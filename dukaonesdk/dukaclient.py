"""Implements a client for making a udp connection to the duka one devices """
import socket
import threading
import time

from socket import SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST

from .device import Device, Mode, Speed
from .dukapacket import DukaPacket
from .responsepacket import ResponsePacket


class DukaClient:
    """Client object for making connection to the duka devices."""

    _mutex = threading.Lock()

    def __init__(self):
        self._devices = {}
        self._sock = None
        self._socket_listening = False

        self._notifyrunning = False
        self._notifythread = threading.Thread(target=self.__notify_fn)
        self._notifythread.start()
        self._found_device_callback = None

    def close(self):
        """Close the client and end the notify thread to end. Wait for the
        thread to end."""
        self._notifyrunning = False
        self._notifythread.join()

    def add_device(
        self,
        device_id: str,
        password: str = None,
        ip_address: str = "<broadcast>",
        onchange=None,
    ) -> Device:
        """Add a new device. If the device already exist the current one will
        be returned"""
        device: Device = self.get_device(device_id)
        if device is None:
            device = Device(device_id, password, ip_address, onchange)
            self._devices[device_id] = device
        packet = DukaPacket()
        packet.initialize_get_firmware_cmd(device)
        self.__send_data(device, packet.data)
        return device

    def remove_device(self, device_id):
        """Remove an existing device"""
        device: Device = self.get_device(device_id)
        if device is not None:
            del self._devices[device_id]
        return device

    def get_device(self, device_id: str) -> Device:
        """Get a device by device id."""
        if device_id not in self._devices:
            return None
        return self._devices[device_id]

    def get_device_count(self):
        """Return the number of devices"""
        return len(self._devices)

    def search_devices(self, callback):
        self._found_device_callback = callback
        packet = DukaPacket()
        packet.initialize_search_cmd()
        self.__wait_for_socket()
        with DukaClient._mutex:
            self._sock.sendto(packet.data, ("<broadcast>", 4000))

    def set_speed(self, device: Device, speed: Speed):
        """Set the speed of the specified device"""
        if device.speed == speed:
            return
        if speed == Speed.OFF:
            self.turn_off(device)
            return
        if device.speed == Speed.OFF:
            self.turn_on(device)
            time.sleep(0.2)

        packet = DukaPacket()
        packet.initialize_speed_cmd(device, speed)
        data = packet.data
        self.__send_data(device, data)

    def set_manual_speed(self, device: Device, manualspeed: int):
        """Set the manual speed of the specified device"""
        if device.speed != Speed.MANUAL:
            self.set_speed(device, Speed.MANUAL)
            time.sleep(0.2)

        packet = DukaPacket()
        packet.initialize_manualspeed_cmd(device, manualspeed)
        data = packet.data
        self.__send_data(device, data)

    def turn_off(self, device: Device):
        """Turn off the specified device"""
        if device.speed == Speed.OFF:
            return
        packet = DukaPacket()
        packet.initialize_off_cmd(device)
        data = packet.data
        self.__send_data(device, data)

    def turn_on(self, device: Device):
        """Turn on the specified device"""
        if device.speed != Speed.OFF:
            return
        packet = DukaPacket()
        packet.initialize_on_cmd(device)
        data = packet.data
        self.__send_data(device, data)

    def set_mode(self, device: Device, mode: Mode):
        """Set the mode of the specified device"""
        if device.mode == Mode:
            return
        packet = DukaPacket()
        packet.initialize_mode_cmd(device, mode)
        data = packet.data
        self.__send_data(device, data)

    def reset_filter_alarm(self, device: Device):
        """Reset the filter alarm"""
        packet = DukaPacket()
        packet.initialize_reset_filter_alarm_cmd(device)
        self.__send_data(device, packet.data)

    def validate_device(
        self, device_id: str, password: str = None, ip_address: str = "<broadcast>"
    ) -> Device:
        """Validate if a device exist and repsonds.
        Returns None if the device does not exist
        Returns the Device object if it exist
        """
        device: Device = self.get_device(device_id)
        # Is the device already added
        if device is not None:
            return device
        device = self.add_device(device_id, password, ip_address)
        try:
            self.__update_device_status(device)
            # 4 sec timeout
            timeout = time.time() + 4
            while True:
                if device.mode is not None:
                    return device
                if time.time() > timeout:
                    break
                time.sleep(0.1)
            return None
        finally:
            self.remove_device(device.device_id)

    def __update_device_status(self, device: Device):
        """Update the device status from the DukaClient
        You should not call this youself
        """
        packet = DukaPacket()
        packet.initialize_status_cmd(device)
        data = packet.data
        self.__send_data(device, data)

    def __update_all_device_status(self):
        """Send an update command to all devices"""
        for device_id in self._devices:
            self.__update_device_status(self._devices[device_id])

    def __send_data(self, device: Device, data):
        """Send a data packet to a device.
        Protect it with a mutex to prevent multiple threads doint it at the
        same time"""
        self.__wait_for_socket()
        with DukaClient._mutex:
            self._sock.sendto(data, (device.ip_address, 4000))

    def __wait_for_socket(self):
        """Wait for notify thread to create socket """
        if self._socket_listening:
            return
        timeout = time.time() + 3
        while True:
            time.sleep(0.1)
            if self._socket_listening:
                return
            if time.time() > timeout:
                raise Exception("Timeout waiting for socket connection")

    def __print_data(self, data):
        """Print data in hex - for debugging purpose """
        print("".join("{:02x}".format(x) for x in data))

    def __open_socket(self):
        """Open the socket and set the  options on the socket"""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.bind(("0.0.0.0", 4000))
        self._sock.settimeout(1.0)
        self._socket_listening = True

    def __close_socket(self):
        """Close the socket"""
        self._socket_listening = False
        try:
            self._sock.close()
            # pylint: disable=bare-except
            # just ignore if closing fails
        except OSError:
            return

    def __open_socket_with_retry(self):
        """Open the socket and retry with 1 sec interval in case of errors
        Skip if notify thread is not running.
        """
        while self._notifyrunning and not self._socket_listening:
            try:
                self.__open_socket()
            except OSError:
                self.__close_socket()
                # wait 1 sec and try again
                time.sleep(1)

    def __receive_data(self):
        """Receive data from the socket.
        If there is a timeout. Send an update command the the devices.
        Return (None, None) where there is no data to process
        """
        try:
            data, addr = self._sock.recvfrom(1024)
            return (data, addr)
        except socket.timeout:
            try:
                self.__update_all_device_status()
            except socket.error:
                # recreate soket on error
                self.__close_socket()
        except socket.error:
            # recreate soket on error
            self.__close_socket()
        return (None, None)

    def __notify_fn(self):
        """Notify thread listening for responses from duka devices.
        This will handle recreating of the socket in case of network errors
        """
        self._notifyrunning = True
        try:
            while self._notifyrunning:
                self.__open_socket_with_retry()
                data, addr = self.__receive_data()
                if data is None:
                    continue
                # print(''.join('{:02x}'.format(x) for x in data))
                packet = ResponsePacket()
                if not packet.initialize_from_data(data):
                    continue
                if packet.device_id not in self._devices:
                    if (
                        packet.search_device_id is not None
                        and self._found_device_callback is not None
                    ):
                        self._found_device_callback(packet.search_device_id)
                    continue
                device: Device = self._devices[packet.device_id]
                ip_address = addr[0]
                self.update_device(device, ip_address, packet)
        finally:
            self.__close_socket()
            self._notifyrunning = False

    def update_device(self, device, ip_address: str, packet: ResponsePacket):
        """Update the device with data recieved. Called by the dukaclient"""
        haschange = False
        if device._ip_address is not None and ip_address != device._ip_address:
            self._ip_address = ip_address
            haschange = True
        if packet.speed is not None and packet.speed != device._speed:
            device._speed = packet.speed
            haschange = True
        if packet.manualspeed is not None and packet.manualspeed != device._manualspeed:
            device._manualspeed = packet.manualspeed
            haschange = True
        if packet.mode is not None and packet.mode != device._mode:
            device._mode = packet.mode
            haschange = True
        if (
            packet.filter_alarm is not None
            and packet.filter_alarm != device._filter_alarm
        ):
            device._filter_alarm = packet.filter_alarm
            haschange = True
        if (
            packet.filter_timer is not None
            and packet.filter_timer != device._filter_timer
        ):
            device._filter_timer = packet.filter_timer
            haschange = True
        if packet.humidity is not None and packet.humidity != device._humidity:
            device._humidity = packet.humidity
            haschange = True
        if packet.firmware_version is not None:
            device._firmware_version = packet.firmware_version
        if packet.firmware_date is not None:
            device._firmware_date = packet.firmware_date
        if packet.unit_type is not None:
            device._unit_type = packet.unit_type
        if haschange and device._changeevent is not None:
            device._changeevent(device)
        # note we do not want the fan rpm to trigger change event because it
        # changes all the time
        if packet.fan1rpm is not None and packet.fan1rpm != device._fan1rpm:
            device._fan1rpm = packet.fan1rpm
        return
