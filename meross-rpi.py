import asyncio
import os
import time
import json

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

configFilePath = '/home/pi/meross.json'
with open(configFilePath, 'r') as f:
    configToBeLoaded = json.load(f)
EMAIL = configToBeLoaded['username']
PASSWORD = configToBeLoaded['password']


async def main():
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    print("got the api client")
    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    print("getting the manager")
    await manager.async_init()
    print("got the manager")

    # Retrieve all the MSS310 devices that are registered on this account
    print("manager async discovery")
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss310")
    print("manager async discovery done")
    
    if len(plugs) < 1:
        print("No MSS310 plugs found...")
    else:
        # Turn it on channel 0
        # Note that channel argument is optional for MSS310 as they only have one channel
        dev = plugs[0]

        # The first time we play with a device, we must update its status
        await dev.async_update()

        # We can now start playing with that
        print(f"Turning on {dev.name}...")
        await dev.async_turn_on(channel=0)
        print("Waiting a bit before turing it off")
        await asyncio.sleep(5)
        print(f"Turing off {dev.name}")
        await dev.async_turn_off(channel=0)

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()