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
    time.sleep(5)
    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    time.sleep(2)
    # Discover devices.
    await manager.async_device_discovery()
    meross_devices = manager.find_devices()
    time.sleep(2)
    # Print them
    print("I've found the following devices:")
    for dev in meross_devices:
        print(f"- {dev.name} ({dev.type}): {dev.online_status}")

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()
    time.sleep(5)

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
