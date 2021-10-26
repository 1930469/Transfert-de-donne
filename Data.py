
import busio #sudo apt-get update THEN sudo apt-get upgrade THEN  sudo apt-get install python3-pip AND sudo pip3 install --upgrade setuptools
import json #sudo apt install libjson-c-dev
import board
import adafruit_tsl2561 #sudo pip3 install adafruit-circuitpython-tsl2561
import time
import RPi.GPIO as GPIO #sudo apt-get install rpi.gpio
import datetime
import random
from w1thermsensor import W1ThermSensor #sudo apt-get install python3-w1thermsensor
from paho.mqtt import client as mqtt_client #pip install paho-mqtt
from configparser import ConfigParser #pip install configparser
sensor = W1ThermSensor()
i2c = busio.I2C(board.SCL, board.SDA)
tsl = adafruit_tsl2561.TSL2561(i2c)
tsl.enable = True
tsl.gain = 0
tsl.integration_time = 1
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.IN)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
config_object = ConfigParser()
config_object.read("config.ini")
capteurinfo = config_object["CapteurInfo"]
ZoneId = capteurinfo["ZoneId"]
TransmitterId = capteurinfo["TransmitterId"]
TimeStamp = datetime.datetime.now().timestamp()
broker = capteurinfo["broker"]
port = int(capteurinfo["port"])
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = capteurinfo["username"]
password = capteurinfo["password"]
sensorIdTemp = capteurinfo["sensorIdTemp"]
sensorIdLum = capteurinfo["sensorIdLum"]
sensorIdMouv = capteurinfo["sensorIdMouv"]
cannalTemp = "local/"+ZoneId+"/"+TransmitterId+"/"+sensorIdTemp+"/temperature"
cannalLum = "local/"+ZoneId+"/"+TransmitterId+"/"+sensorIdLum+"/luminosite"
cannalMouv = "local/"+ZoneId+"/"+TransmitterId+"/"+sensorIdMouv+"/mouvement"

 

def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
                if rc == 0:
                        print("Connected to MQTT Broken!")
                else:
                        print("Failed to connect")
        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        print("Test 1: Reussi")
        return client

 

def publish(client):
        while True:
                d = datetime.datetime.now()
                temperature = sensor.get_temperature()
                celsius = round(temperature, 1)
                lux = tsl.lux
                lumiere = round(lux)
                date = d.strftime("%Y/%m/%d %H:%M:%S")
                i = GPIO.input(27)
                if i==0:
                        GPIO.output(22 ,1)
                        GPIO.output(23, 0)
                elif i==1:
                        GPIO.output(23, 1)
                        GPIO.output(22, 0)
                hot = '{"SentDate":"'+date+'","ValueType":"float","value":'+str(celsius)+',"DataType":"Temperature"}'
                mouv = '{"SentDate":"'+date+'","ValueType":"bool","value":'+str(i)+',"DataType":"Mouvement"}'
                lum = '{"SentDate":"'+date+'","ValueType":"integer","value":'+str(lumiere)+',"DataType":"Luminosite"}'
                print(hot)
                print(mouv)
                print(lum)
                result1 = client.publish(cannalTemp,hot)
                result2 = client.publish(cannalMouv,mouv)
                result3 = client.publish(cannalLum,lum)

 

def run():
        print("run")
        client = connect_mqtt()
        client.loop_start()
        publish(client)

 

if __name__ == "__main__":
        run()
