import asyncio
import RPi.GPIO as GPIO
import time
import threading
import logging
import os
import subprocess
import json
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from gpio import GpioManager

appname = 'merross-rpi'
folderPath = '/home/pi/'
os.makedirs(folderPath + "logs/", exist_ok=True)
logging.basicConfig(format='%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(
                            folderPath + "logs/"+appname+".log"),
                        logging.StreamHandler()
                    ])
logging.info("Starting " + appname)

configFilePath = '/home/pi/meross.json'
with open(configFilePath, 'r') as f:
    configToBeLoaded = json.load(f)
EMAIL = configToBeLoaded['username']
PASSWORD = configToBeLoaded['password']

exitapp = False

gpioManager = GpioManager("test")

googleHostForInternetCheck = "8.8.8.8"
def haveInternet():
    try:
        output = subprocess.check_output(
            "ping -c 1 {}".format(googleHostForInternetCheck), shell=True)

    except Exception:
        return False

    return True


async def main():
    logging.info("in async def main")

    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 10, requests_per_second_limit = 10)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()
    plugs = manager.find_devices()

    fredbike = "notSet"
    amybike = "notSet"
    windowfan = "notSet"
    roomfan = "notSet"

    for dev in plugs:
        logging.info(f"- {dev.name} ({dev.type}): {dev.online_status}")
        if(dev.name == "fredbike"):
            fredbike = dev
            logging.info(f"found fredbike {fredbike}")
        
        if(dev.name == "amybike"):
            amybike = dev
            logging.info(f"found amybike {amybike}")
        
        if(dev.name == "windowfan"):
            windowfan = dev
            logging.info(f"found windowfan {windowfan}")
        
        if(dev.name == "roomfan"):
            roomfan = dev
            logging.info(f"found roomfan {roomfan}")

    isFanRoomOn = False
    isFanWindowOn = False
    isBikeAmyOn = False
    isBikeFredOn = False

    timeFanRoomPushed = 0
    timeFanWindowPushed = 0
    timeBikeFredPushed = 0
    timeBikeAmyPushed = 0
    timestampInternetCheck = 0

    logging.info("starting while loop")
    while not exitapp: 

        timestampNow = time.time()

        
        internetWasLost = False
        if(timestampNow - timestampInternetCheck > 5):
            logging.info("checking internet")
            while(not haveInternet()):
                internetWasLost = True
                logging.info("internet is not available, sleeping 1 second")
                time.sleep(1)
            timestampInternetCheck = timestampNow

        if(internetWasLost):
            logging.info(
                "internet is back, resetting the merross")
            manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 10, requests_per_second_limit = 10)
            await manager.async_init()
            logging.info(
                "reset done of the merross")
            

        buttonName = "fanRoom"
        if gpioManager.isButtonPushed("fanRoom") and roomfan is not "notSet":
            if timeFanRoomPushed < timestampNow - 1:
                logging.info(buttonName + " button was pushed!")
                timeFanRoomPushed = timestampNow
                if(isFanRoomOn):
                    await roomfan.async_turn_off(channel=0)
                    gpioManager.setLed(buttonName, False)
                    isFanRoomOn = False
                else:
                    await roomfan.async_turn_on(channel=0)
                    gpioManager.setLed(buttonName, True)
                    isFanRoomOn = True
                

        buttonName = "fanWindow"
        if gpioManager.isButtonPushed("fanWindow") and windowfan is not "notSet":
            if timeFanWindowPushed < timestampNow - 1:
                logging.info(buttonName + " button was pushed!")
                timeFanWindowPushed = timestampNow
                if(isFanWindowOn):
                    await windowfan.async_turn_off(channel=0)
                    gpioManager.setLed(buttonName, False)
                    isFanWindowOn = False
                else:
                    await windowfan.async_turn_on(channel=0)
                    gpioManager.setLed(buttonName, True)
                    isFanWindowOn = True
                
        buttonName = "bikeFred"
        if gpioManager.isButtonPushed("bikeFred") and fredbike is not "notSet":
            if timeBikeFredPushed < timestampNow - 1:
                logging.info(buttonName + " button was pushed!")
                timeBikeFredPushed = timestampNow
                if(isBikeFredOn):
                    await fredbike.async_turn_off(channel=0)
                    gpioManager.setLed(buttonName, False)
                    isBikeFredOn = False
                else:
                    await fredbike.async_turn_on(channel=0)
                    gpioManager.setLed(buttonName, True)
                    isBikeFredOn = True

        
        buttonName = "bikeAmy"
        if gpioManager.isButtonPushed(buttonName)  and amybike is not "notSet":
            if timeBikeAmyPushed < timestampNow - 1:
                logging.info(buttonName + " button was pushed!")
                timeBikeAmyPushed = timestampNow
                if(isBikeAmyOn):
                    await amybike.async_turn_off(channel=0)
                    gpioManager.setLed(buttonName, False)
                    isBikeAmyOn = False
                else:
                    await amybike.async_turn_on(channel=0)
                    gpioManager.setLed(buttonName, True)
                    isBikeAmyOn = True
        time.sleep(0.2)

    logging.info("Shutting down!")
    manager.close()
    await http_api_client.async_logout()
    GPIO.cleanup()
    logging.info("Shutdown complete!")

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

