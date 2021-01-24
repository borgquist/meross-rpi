import RPi.GPIO as GPIO

class GpioManager:
    name = ""
    def __init__(self, name):
        self.name = name
    
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

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    class Button:
        buttonPin = 0
        ledPin = 0
        name = ""
        timestampPushed = 0
        def __init__(self, bPin, lPin, n):
            self.buttonPin = bPin
            self.ledPin = lPin
            self.name = n
        def __str__(self):
            return "name [" + str(self.name) + "] buttonPin [" + str(self.buttonPin) + "] ledPin [" + str(self.ledPin) + "]"


    bikeFred = Button(bikeFredPin, bikeLedFredPin, "bikeFred")
    bikeAmy = Button(bikeAmyPin, bikeLedAmyPin, "bikeAmy")
    fanRoom = Button(fanRoomPin, fanRoomLedPin, "fanRoom")
    fanWindow = Button(fanWindowPin, fanWindowLedPin, "fanWindow")

    def getButton(self, buttonName):
        if(buttonName == "bikeFred"):
            return self.bikeFred
        if(buttonName == "bikeAmy"):
            return self.bikeAmy
        if(buttonName == "fanWindow"):
            return self.fanWindow
        if(buttonName == "fanRoom"):
            return self.fanRoom
        return 0


    def isButtonPushed(self, buttonName):
        button = self.getButton(buttonName)
        if GPIO.input(button.buttonPin) == GPIO.HIGH:
            return True
        return False

    def setLed(self, buttonName, setOn):
        button = self.getButton(buttonName)
        if(setOn):
            GPIO.output(button.ledPin, GPIO.HIGH)
        else:
            GPIO.output(button.ledPin, GPIO.LOW)
                    
            
