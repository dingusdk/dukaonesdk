"""
Create a file called ".deviceid" in the current folder.
This file should contain  the duka one device id.
You can see the duka one device id in the duka one app.
"""

import asyncio
import sys

from dukaonesdk.device import Device, Mode
from dukaonesdk.dukaclient import DukaClient


def onchange(device: Device):
    """Callback function when device changes"""
    print(
        f"ip: {device.ip_address}"
        f" speed: {device.speed},"
        f" manualspeed: {device.manualspeed},"
        f" fan1rpm: {device.fan1rpm},"
        f" mode: {device.mode},"
        f" humidity: {device.humidity},"
        f" filter alarm: {device.filter_alarm},"
        f" filter timer; {device.filter_timer} minutes"
    )


async def main():
    """Main example"""
    client: DukaClient = DukaClient()
    device_ids = await client.search_devices_async()
    print(f"Found {len(device_ids)} devices")
    for deviceid in device_ids:
        print(f"Device id: {deviceid}")

    # read the device id
    with open(".deviceid", "r") as file:
        device_id = file.readline().replace("\n", "")
    # initialize the DukaClient and add the device
    mydevice: Device = client.validate_device(device_id, ip_address="255.255.255.255")
    if mydevice is None:
        print("Device does not respond")
    else:
        mydevice = client.add_device(
            device_id, ip_address=mydevice.ip_address, onchange=onchange
        )
        print("Device added")
        if not await client.wait_for_initialize_async(mydevice):
            print("Device not initialized")

        print(f"Firmware version: {mydevice.firmware_version}")
        print(f"Firmware date: {mydevice.firmware_date}")
        print(f"Unit type: {mydevice.unit_type}")
        while True:
            print(
                "Press one key and enter. "
                "1-3 for speed, 0=off, 9=on,b,n,m for mode,"
                " f for reset filter alarm, q for quit"
            )
            char = sys.stdin.read(2)[0]
            if char == "q":
                break
            if char >= "0" and char <= "3":
                client.set_speed(mydevice, ord(char) - ord("0"))
            if char >= "4" and char <= "8":
                manualspeed = ((ord(char) - ord("4")) * 50) + 50
                client.set_manual_speed(mydevice, manualspeed)
            if char == "9":
                client.turn_on(mydevice)
            if char == "b":
                client.set_mode(mydevice, Mode.ONEWAY)
            if char == "n":
                client.set_mode(mydevice, Mode.TWOWAY)
            if char == "m":
                client.set_mode(mydevice, Mode.IN)
            if char == "f":
                client.reset_filter_alarm(mydevice)

    print("Closing")
    client.close()
    print("Done")

    sys.exit(0)


asyncio.run(main())
