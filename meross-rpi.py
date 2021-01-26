import asyncio
import RPi.GPIO as GPIO
import time
import logging
import subprocess
import json
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from gpio import GpioManager
from os import remove
from os.path import exists
import traceback
import signal
import functools


def haveInternet():
    googleHostForInternetCheck = "8.8.8.8"
    try:
        output = subprocess.check_output(
            "ping -c 5 {}".format(googleHostForInternetCheck), shell=True)

    except Exception:
        return False

    return True


devBikeFred = "notSet"
devBikeAmy = "notSet"
devFanWindow = "notSet"
devFanRoom = "notSet"


internetIsLost = False
async def checkInternet(loop):
    logger = logging.getLogger('merosslogger')
    # global doReset
    global internetIsLost
    logger.info("checking internet")
    try:
        while(True):
            while(not haveInternet()):
                internetIsLost = True
                logger.info("internet is not available, sleeping 1 second")
                await asyncio.sleep(1, loop=loop)
            
            if internetIsLost:
                logger.info("internet is back")
                #doReset = True
                internetIsLost = False
                
            await asyncio.sleep(3, loop=loop)
    except asyncio.CancelledError:
        logger.info("asyncio.CancelledError, in checkInternet")
        return "checkInternet cancelled"
                
    


async def main(loop):
    global devBikeFred 
    global devBikeAmy 
    global devFanWindow
    global devFanRoom 
    global internetIsLost
    logger = logging.getLogger('merosslogger')
    
    gpioManager = GpioManager("test")

    
    doReset = True
    firstRun = True
    logger.info("recreating http client")
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    logger.info("recreating manager")
    manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 4, requests_per_second_limit = 2)
    logger.info("doing manager.async_init")
    
    
    isFanRoomOn = False
    isFanWindowOn = False
    isBikeAmyOn = False
    isBikeFredOn = False

    timeFanRoomPushed = 0
    timeFanWindowPushed = 0
    timeBikeFredPushed = 0
    timeBikeAmyPushed = 0

    fanRoomPin = 27
    fanWindowPin = 23
    bikeFredPin = 5
    bikeAmyPin = 17
    exitapp = False
    logger.info("starting while loop")
    while not exitapp: 
        try:
            await asyncio.sleep(0.2, loop=loop)
            
            # first time is created and then afterwards this is a reset
            if(doReset and not internetIsLost):
                doReset = False
                if firstRun:
                    logger.info("firstrun so skipping manager and http in loop")
                else:
                    logger.info("recreating http client")
                    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
                    logger.info("recreating manager")
                    manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 4, requests_per_second_limit = 2)
                    logger.info("doing manager.async_init")
                    
                await manager.async_init()
                logger.info("doing async update")

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
                
                await devBikeFred.async_update()
                await devBikeAmy.async_update()
                await devFanWindow.async_update()
                await devFanRoom.async_update()
                if(not firstRun):
                    logger.info("done doing async update, sleeping 3 seconds to prevent races")
                    await asyncio.sleep(3, loop=loop)

                
            
            timestampNow = time.time()

            buttonName = "fanRoom"
            if gpioManager.isButtonPinPushed(fanRoomPin):
                if(internetIsLost):
                    logger.info("not processing " + buttonName + " button press since internet is lost")
                elif timeFanRoomPushed < timestampNow - 0.5:
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
            if gpioManager.isButtonPinPushed(fanWindowPin):
                if(internetIsLost):
                    logger.info("not processing " + buttonName + " button press since internet is lost")
                elif timeFanWindowPushed < timestampNow - 0.5:
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
            if gpioManager.isButtonPinPushed(bikeFredPin):
                if(internetIsLost):
                    logger.info("not processing " + buttonName + " button press since internet is lost")
                elif timeBikeFredPushed < timestampNow - 0.5:
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

            
            buttonName = "bikeAmy"
            if gpioManager.isButtonPinPushed(bikeAmyPin):
                if(internetIsLost):
                    logger.info("not processing " + buttonName + " button press since internet is lost")
                elif timeBikeAmyPushed < timestampNow - 0.5:
                    logger.info(buttonName + " button was pushed!")
                    timeBikeAmyPushed = timestampNow
                    if(isBikeAmyOn):
                        await devBikeAmy.async_turn_off(channel=0)
                        gpioManager.setLed(buttonName, False)
                        isBikeAmyOn = False
                    else:
                        await devBikeAmy.async_turn_on(channel=0)
                        gpioManager.setLed(buttonName, True)
                        isBikeAmyOn = True
            firstRun = False
            
        except asyncio.CancelledError:
            logger.info("CancelledError received")
            try:
                manager.close()
                logger.info("Manager closed")
            except UnboundLocalError:
                logger.info("manager doesn't exist")
            try:
                await http_api_client.async_logout()
                logger.info("http_api_client.async_logout")
            except UnboundLocalError:
                logger.info("http_api_client doesn't exist")
            
            return "main cancelled in except"

        except Exception as err:
            logger.error("exception in main " + traceback.format_exc())
            doReset = True
            try:
                manager.close()
                logger.info("Manager closed")
            except UnboundLocalError:
                logger.info("manager doesn't exist")
            try:
                await http_api_client.async_logout()
                logger.info("http_api_client.async_logout")
            except UnboundLocalError:
                logger.info("http_api_client doesn't exist")

    logger.info("Shutting down!")
    try:
        manager.close()
        logger.info("Manager closed")
    except UnboundLocalError:
        logger.info("manager doesn't exist")
    try:
        await http_api_client.async_logout()
        logger.info("http_api_client.async_logout")
    except UnboundLocalError:
        logger.info("http_api_client doesn't exist")
    GPIO.cleanup()
    logger.info("Shutdown complete!")
    return "main cancelled"


def setup_logger(logger_name, log_file, level=logging.INFO):
    # # Erase log if already exists
    # if exists(log_file):
    #     remove(log_file)
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

async def shutdown(sig, loop):
    print('caught {0}'.format(sig.name))
    tasks = [task for task in asyncio.Task.all_tasks() if task is not
             asyncio.tasks.Task.current_task()]
    list(map(lambda task: task.cancel(), tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print('finished awaiting cancelled tasks, results: {0}'.format(results))
    loop.stop()
 

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

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(loop), loop=loop)
    # asyncio.ensure_future(checkInternet(loop), loop=loop)
    loop.add_signal_handler(signal.SIGTERM,
                            functools.partial(asyncio.ensure_future,
                                            shutdown(signal.SIGTERM, loop)))
    loop.add_signal_handler(signal.SIGINT,
                            functools.partial(asyncio.ensure_future,
                                            shutdown(signal.SIGTERM, loop)))

    try:
        loop.run_forever()
    finally:
        loop.close()
        logger.info("loop closed")
    

