import asyncio
import RPi.GPIO as GPIO
import time
import logging
import socket
import subprocess
import json
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from gpio import GpioManager
from os import remove
from os.path import exists
import traceback
import threading


def haveInternet():
    googleHostForInternetCheck = "8.8.8.8"
    try:
        output = subprocess.check_output(
            "ping -c 1 {}".format(googleHostForInternetCheck), shell=True)

    except Exception:
        return False

    return True




devBikeFred = "notSet"
devBikeAmy = "notSet"
devFanWindow = "notSet"
devFanRoom = "notSet"
exitapp = False

async def getPlugs(manager):
    global devBikeFred 
    global devBikeAmy 
    global devFanWindow
    global devFanRoom 
    global doReset
    await manager.async_init()
    logger = logging.getLogger('merosslogger')
    
    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()
    plugs = manager.find_devices()

    for dev in plugs:
        logger.info(f"- {dev.name} ({dev.type}): {dev.online_status}")
        if(dev.name == "fredbike"):
            devBikeFred = dev
            logger.info(f"found fredbike {devBikeFred}")
        
        if(dev.name == "amybike"):
            devBikeAmy = dev
            logger.info(f"found devBikeAmy {devBikeAmy}")
        
        if(dev.name == "windowfan"):
            devFanWindow = dev
            logger.info(f"found devFanWindow {devFanWindow}")
        
        if(dev.name == "roomfan"):
            devFanRoom = dev
            logger.info(f"found devFanRoom {devFanRoom}")
    doReset = False

async def shutdownPlugs(manager, http_api_client):
    manager.close()
    await http_api_client.async_logout()

doReset = False
def thread_internet(name):
    logger = logging.getLogger('merosslogger')
    
    while not exitapp:
        try:
            time.sleep(1)
            logger.info("checking internet")
            internetWasLost = False
            while(not haveInternet()):
                internetWasLost = True
                logger.info("internet is not available, sleeping 1 second")
                time.sleep(1)
            
            if(internetWasLost):
                logger.info(
                    "internet is back, resetting the stream to firebase")
                doReset = True

        except Exception as err:
            logger.error("exception " + traceback.format_exc())

    logger.info("thread_time    : exiting")


async def main():
    global devBikeFred 
    global devBikeAmy 
    global devFanWindow
    global devFanRoom 
    global doReset
    logger = logging.getLogger('merosslogger')
    
    gpioManager = GpioManager("test")

    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 10, requests_per_second_limit = 10)
    
    await getPlugs(manager)

    isFanRoomOn = False
    isFanWindowOn = False
    isBikeAmyOn = False
    isBikeFredOn = False

    timeFanRoomPushed = 0
    timeFanWindowPushed = 0
    timeBikeFredPushed = 0
    timeBikeAmyPushed = 0
    timestampInternetCheck = 0

    logger.info("starting while loop")
    while not exitapp: 
        try:
            if(doReset):
                logger.info("calling getplugs to do a reaset")
                await getPlugs(manager)
                doReset = False

            timestampNow = time.time()

            buttonName = "fanRoom"
            if gpioManager.isButtonPushed("fanRoom"):
                if timeFanRoomPushed < timestampNow - 1:
                    logger.info(buttonName + " button was pushed!")
                    timeFanRoomPushed = timestampNow
                    if(isFanRoomOn):
                        await devFanRoom.async_turn_off(channel=0)
                        gpioManager.setLed(buttonName, False)
                        isFanRoomOn = False
                    else:
                        await devFanRoom.async_turn_on(channel=0)
                        gpioManager.setLed(buttonName, True)
                        isFanRoomOn = True
                    

            buttonName = "fanWindow"
            if gpioManager.isButtonPushed("fanWindow"):
                if timeFanWindowPushed < timestampNow - 1:
                    logger.info(buttonName + " button was pushed!")
                    timeFanWindowPushed = timestampNow
                    if(isFanWindowOn):
                        await devFanWindow.async_turn_off(channel=0)
                        gpioManager.setLed(buttonName, False)
                        isFanWindowOn = False
                    else:
                        await devFanWindow.async_turn_on(channel=0)
                        gpioManager.setLed(buttonName, True)
                        isFanWindowOn = True
                    
            buttonName = "bikeFred"
            if gpioManager.isButtonPushed("bikeFred"):
                if timeBikeFredPushed < timestampNow - 1:
                    logger.info(buttonName + " button was pushed!")
                    timeBikeFredPushed = timestampNow
                    if(isBikeFredOn):
                        await devBikeFred.async_turn_off(channel=0)
                        gpioManager.setLed(buttonName, False)
                        isBikeFredOn = False
                    else:
                        await devBikeFred.async_turn_on(channel=0)
                        gpioManager.setLed(buttonName, True)
                        isBikeFredOn = True

            
            if gpioManager.isButtonPushed("bikeAmy"):
                if timeBikeAmyPushed < timestampNow - 1:
                    logger.info("bikeAmy" + " button was pushed!")
                    timeBikeAmyPushed = timestampNow
                    if(isBikeAmyOn):
                        await devBikeAmy.async_turn_off(channel=0)
                        gpioManager.setLed("bikeAmy", False)
                        isBikeAmyOn = False
                    else:
                        await devBikeAmy.async_turn_on(channel=0)
                        gpioManager.setLed("bikeAmy", True)
                        isBikeAmyOn = True
            
            asyncio.sleep(0.2)
            
        except Exception as err:
            logger.error("exception in main " + traceback.format_exc())

    logger.info("Shutting down!")
    await shutdownPlugs(manager, http_api_client)
    logger.info("Plugs shut down")
    GPIO.cleanup()
    logger.info("Shutdown complete!")


def setup_logger(logger_name, log_file, level=logging.INFO):
    # Erase log if already exists
    if exists(log_file):
        remove(log_file)
    # Configure log file
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


if __name__ == '__main__':

    appname = 'meross'
    folderPath = '/home/pi/'

    configFilePath = '/home/pi/config_meross.json'
    with open(configFilePath, 'r') as f:
        configToBeLoaded = json.load(f)
    EMAIL = configToBeLoaded['username']
    PASSWORD = configToBeLoaded['password']
    setup_logger('merosslogger', '/home/pi/meross.log')
    logger = logging.getLogger('merosslogger')
    


    logger.info("Starting " + appname)
    logger.info("in async def main")
    
    internetThread = threading.Thread(target=thread_internet, args=(1,))
    internetThread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    logger.info("loop closed")

