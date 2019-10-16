from gpiozero import Button, LED
import paho.mqtt.client as mqtt
from time import sleep
import os

mqtt_user = os.environ["MQTT_USER"]
mqtt_passwd = os.environ["MQTT_PASSWD"]
mqtt_host = os.environ["MQTT_HOST"]

sensor_north = Button(12, bounce_time=3)
sensor_south = Button(16, bounce_time=3)

# Use LED to utilize blink() to pulse the relay
relay_north = LED(5, active_high=False)
relay_south = LED(6, active_high=False)

client = mqtt.Client()
client.username_pw_set(mqtt_user, password=mqtt_passwd)
client.connect(mqtt_host)

# Required to allow the state of the doors to be learned upon startup
north_state = "unset"
south_state = "unset"

# Report the state of the door via MQTT
def report_state(door, state):
    print(f"topic=stat/garage/{door} payload={state}")
    client.publish(f"stat/garage/{door}", payload=state, qos=1, retain=True)


# Trigger a relay pulse to open or close the door based on the door name
def door_button(name):
    print(f"The {name} door relay was activated")
    if name == "north":
        relay_north.blink(on_time=0.5, n=1, background=True)
    elif name == "south":
        relay_south.blink(on_time=0.5, n=1, background=True)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("cmnd/garage/north")
    client.subscribe("cmnd/garage/south")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload}")
    if msg.topic == "cmnd/garage/north":
        door_button("north")
    elif msg.topic == "cmnd/garage/south":
        door_button("south")


# Determines if the door state has changed
def check_door(door, sensor, state):
    if sensor == True and (state == "open" or state == "unset"):
        state = "closed"
        report_state(door, state)
    elif sensor == False and (state == "open" or state == "unset"):
        state = "open"
        report_state(door, state)
    return state


client.on_connect = on_connect
client.on_message = on_message
sleep(3)

while True:
    client.loop()
    north_state = check_door("north", sensor_north.is_pressed, north_state)
    south_state = check_door("south", sensor_south.is_pressed, south_state)
