import RPi.GPIO as GPIO
import time
import threading
import asyncio
import os
import json
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

configFilePath = '/home/pi/meross.json'
with open(configFilePath, 'r') as f:
    configToBeLoaded = json.load(f)
EMAIL = configToBeLoaded['username']
PASSWORD = configToBeLoaded['password']

lastServerHeartBeat = time.time()
exitapp = False

fredbike = ""
amybike = ""
windowfan = ""
roomfan = ""

fanRoomPin = 27
fanWindowPin = 23
bikeFredPin = 5
bikeAmyPin = 17

bikeLedFredPin = 6
bikeLedAmyPin = 25
fanRoomLedPin = 16
fanWindowLedPin = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(fanRoomPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(fanWindowPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(bikeFredPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(bikeAmyPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

GPIO.setup(bikeLedFredPin, GPIO.OUT)
GPIO.setup(bikeLedAmyPin, GPIO.OUT)
GPIO.setup(fanRoomLedPin, GPIO.OUT)
GPIO.setup(fanWindowLedPin, GPIO.OUT)

timestampNow = time.time()
timeFanRoomPushed = timestampNow + 5
timeFanWindowPushed = timestampNow + 5
timeBikeFredPushed = timestampNow + 5
timeBikeAmyPushed = timestampNow + 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


async def main():
    try:
        http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
        # Setup and start the device manager
        manager = MerossManager(http_client=http_api_client, burst_requests_per_second_limit = 10, requests_per_second_limit = 10)
        await manager.async_init()

        # Retrieve all the MSS310 devices that are registered on this account
        await manager.async_device_discovery()
        plugs = manager.find_devices()

        isFanRoomOn = False
        isFanWindowOn = False
        isBikeAmyOn = False
        isBikeFredOn = False

        timeFanRoomPushed = 0
        timeFanWindowPushed = 0
        timeBikeFredPushed = 0
        timeBikeAmyPushed = 0
        
        while not exitapp: 
            if GPIO.input(fanRoomPin) == GPIO.HIGH:
                timestampNow = time.time()
                if timeFanRoomPushed < timestampNow - 1:
                    print("fanRoomPin button was pushed!")
                    print("time since last ", timestampNow - timeFanRoomPushed)
                    timeFanRoomPushed = timestampNow
                    if(isFanRoomOn):
                        await roomfan.async_turn_on(channel=0)
                        GPIO.output(fanRoomLedPin,GPIO.LOW)
                        isFanRoomOn = False
                    else:
                        await roomfan.async_turn_off(channel=0)
                        GPIO.output(fanRoomLedPin,GPIO.HIGH)
                        isFanRoomOn = True
                    
    
            if GPIO.input(fanWindowPin) == GPIO.HIGH:
                timestampNow = time.time()
                if timeFanWindowPushed < timestampNow - 1:
                    print("fanWindowPin button was pushed!")
                    print("time since last ", timestampNow - timeFanWindowPushed)
                    timeFanWindowPushed = timestampNow
                    if(isFanWindowOn):
                        await windowfan.async_turn_on(channel=0)
                        GPIO.output(fanWindowLedPin,GPIO.LOW)
                        isFanWindowOn = False
                    else:
                        await windowfan.async_turn_off(channel=0)
                        GPIO.output(fanWindowLedPin,GPIO.HIGH)
                        isFanWindowOn = True
                    
            if GPIO.input(bikeFredPin) == GPIO.HIGH:
                timestampNow = time.time()
                if timeBikeFredPushed < timestampNow - 1:
                    print("bikeFredPin button was pushed!")
                    print("time since last ", timestampNow - timeBikeFredPushed)
                    timeBikeFredPushed = timestampNow
                    if(isBikeFredOn):
                        await fredbike.async_turn_on(channel=0)
                        GPIO.output(bikeLedFredPin,GPIO.LOW)
                        isBikeFredOn = False
                    else:
                        await fredbike.async_turn_off(channel=0)
                        GPIO.output(bikeLedFredPin,GPIO.HIGH)
                        isBikeFredOn = True
    
            if GPIO.input(bikeAmyPin) == GPIO.HIGH:
                timestampNow = time.time()
                if timeBikeAmyPushed < timestampNow - 1:
                    print("bikeAmyPin button was pushed!")
                    print("time since last ", timestampNow - timeBikeAmyPushed)
                    timeBikeAmyPushed = timestampNow
                    if(isBikeAmyOn):
                        await amybike.async_turn_on(channel=0)
                        GPIO.output(bikeLedAmyPin,GPIO.LOW)
                        isBikeAmyOn = False
                    else:
                        await amybike.async_turn_off(channel=0)
                        GPIO.output(bikeLedAmyPin,GPIO.HIGH)
                        isBikeAmyOn = True
            time.sleep(0.1)
    finally:
        print("Shutting down!")
        manager.close()
        await http_api_client.async_logout()
        GPIO.cleanup()
        manager.close()
        await http_api_client.async_logout()
        print("Shutdown complete!")
 


