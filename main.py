from gpiozero import Button, LED
import paho.mqtt.client as mqtt
from time import sleep
import os

mqtt_user = os.environ["MQTT_USER"]
mqtt_passwd = os.environ["MQTT_PASSWD"]
mqtt_host = os.environ["MQTT_HOST"]

sensor_north = Button(12, bounce_time=3)
sensor_south = Button(16, bounce_time=3)

north_state = ""
south_state = ""

# Use LED to utilize blink() to pulse the relay
relay_north = LED(5, active_high=False)
relay_south = LED(6, active_high=False)

client = mqtt.Client()
client.username_pw_set(mqtt_user, password=mqtt_passwd)
client.connect(mqtt_host)


def door_state(name, state):
    print(f"topic=stat/garage/{name} payload={state}")
    client.publish(f"stat/garage/{name}", payload=state, qos=1, retain=True)


def door_button(name):
    print(f"The {name} door relay was activated")
    if name == "north":
        relay_north.blink(on_time=0.5, n=1, background=True)
    if name == "south":
        relay_south.blink(on_time=0.5, n=1, background=True)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("cmnd/garage/north")
    client.subscribe("cmnd/garage/south")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.payload))
    print(f"{msg.topic} {msg.payload}")
    if msg.topic == "cmnd/garage/north":
        door_button("north")
    if msg.topic == "cmnd/garage/south":
        door_button("south")


def door_north():
    global north_state
    name = "north"
    if sensor_north.is_pressed == True and north_state == "":
        north_state = "closed"
        door_state(name, north_state)
    elif sensor_north.is_pressed == False and north_state == "":
        north_state = "open"
        door_state(name, north_state)
    elif sensor_north.is_pressed == True and north_state == "open":
        north_state = "closed"
        door_state(name, north_state)
    elif sensor_north.is_pressed == False and north_state == "closed":
        north_state = "open"
        door_state(name, north_state)


def door_south():
    global south_state
    name = "south"
    if sensor_south.is_pressed == True and south_state == "":
        south_state = "closed"
        door_state(name, south_state)
    elif sensor_south.is_pressed == False and south_state == "":
        south_state = "open"
        door_state(name, south_state)
    elif sensor_south.is_pressed == True and south_state == "open":
        south_state = "closed"
        door_state(name, south_state)
    elif sensor_south.is_pressed == False and south_state == "closed":
        south_state = "open"
        door_state(name, south_state)


client.on_connect = on_connect
client.on_message = on_message

# Give the mqtt client time to connect
sleep(3)

while True:
    client.loop(0.1)
    door_north()
    door_south()
