import logging
import os

appname = 'testlog'
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
