"""
Create a file called ".deviceid" in the current folder.
This file should contain  the duka one device id.
You can see the duka one device id in the duka one app.
"""
import sys

from dukaonesdk.dukaclient import DukaClient
from dukaonesdk.device import Device, Mode


def onchange(device: Device):
    """Callback function when device changes"""
    print(f"ip: {device.ip_address} speed: {device.speed}, mode: {device.mode}")

def main():
    """Main example """
    # read the device id
    with open('.deviceid', 'r') as file:
        device_id = file.readline().replace('\n', '')
    # initialize the DukaClient and add the device
    client: DukaClient = DukaClient()
    mydevice: Device = client.validate_device(device_id)
    if mydevice is None:
        print("Device does not respond")
        return

    mydevice = client.add_device(device_id, ip_address=mydevice.ip_address, onchange=onchange)
    print("Device added")

    while True:
        print("Press one key and enter. 1-3 for speed, 0 for off,b,n,m for mode, q for quit")
        char = sys.stdin.read(2)[0]
        if char == 'q':
            break
        if char >= '0' and char <= '3':
            client.set_speed(mydevice, ord(char) - ord('0'))
        if char == '9':
            client.turn_on(mydevice)
        if char == 'b':
            client.set_mode(mydevice, Mode.ONEWAY)
        if char == 'n':
            client.set_mode(mydevice, Mode.TWOWAY)
        if char == 'm':
            client.set_mode(mydevice, Mode.IN)

    print("Closing")
    client.close()
    print("Done")

    exit(0)

main()
