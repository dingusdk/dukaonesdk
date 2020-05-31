"""Implements a client for making a udp connection to the duka one devices """
import socket
import threading
import time

from socket import SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST

from .device import Device, Mode, Speed
from .dukapacket import DukaPacket

class DukaClient:
    """Client object for making connection to the duka devices."""
    _mutex = threading.Lock()

    def __init__(self):
        self._devices = {}
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._notifyrunning = False
        self._notifythread = threading.Thread(target=self.__notify_fn)
        self._notifythread.start()

    def close(self):
        """Close the client and end the notify thread. Wait for the thread to end."""
        self._notifyrunning = False
        self._notifythread.join()

    def add_device(self, device_id: str, password: str = None,
                   ip_address: str = "<broadcast>", onchange=None) -> Device:
        """Add a new device."""
        device: Device = Device(device_id, password, ip_address, onchange)
        self._devices[device_id] = device
        return device

    def get_device(self, device_id: str) -> Device:
        """Get a device by device id."""
        if not device_id in self._devices:
            return None
        return self._devices[device_id]

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

    def turn_off(self, device: Device):
        """Turn off the specified device"""
        packet = DukaPacket()
        packet.initialize_off_cmd(device)
        data = packet.data
        self.__send_data(device, data)


    def turn_on(self, device: Device):
        """Turn on the specified device"""
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

    def __update_device_status(self, device: Device):
        """ Update the device status from the DukaClient
            You should not call this youself
        """
        packet = DukaPacket()
        packet.initialize_status_cmd(device)
        data = packet.data
        self.__send_data(device, data)

    def __update_all_device_status(self):
        for device_id in self._devices:
            self.__update_device_status(self._devices[device_id])

    def __send_data(self, device: Device, data):
        with DukaClient._mutex:
            self._sock.sendto(data, (device.ip_address, 4000))

    def __print_data(self, data):
        """Print data in hex - for debugging purpose """
        print(''.join('{:02x}'.format(x) for x in data))


    def __notify_fn(self):
        self._notifyrunning = True
        self._sock.bind(("0.0.0.0", 4000))
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self._sock.settimeout(1.0)
        while self._notifyrunning:
            try:
                data, addr = self._sock.recvfrom(1024)
            except socket.timeout:
                self.__update_all_device_status()
                continue
            packet = DukaPacket()
            if not packet.initialize_from_data(data):
                continue
            if not packet.is_response_from_device():
                continue
            device_id = packet.response_device_id()
            if device_id not in self._devices:
                continue
            device: Device = self._devices[device_id]
            ip_address = addr[0]
            speed = packet.response_speed()
            if not packet.response_is_on():
                speed = Speed.OFF
            mode = packet.response_mode()
            device.update(ip_address, speed, mode)
        self._sock.close()
