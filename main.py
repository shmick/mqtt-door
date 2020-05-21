from gpiozero import LineSensor, LED
import paho.mqtt.client as mqtt
from time import sleep
import json
import os

mqtt_user = os.environ["MQTT_USER"]
mqtt_passwd = os.environ["MQTT_PASSWD"]
mqtt_host = os.environ["MQTT_HOST"]

sensor_north = LineSensor(12, pull_up=True, queue_len=50)
sensor_south = LineSensor(16, pull_up=True, queue_len=50)

# Use LED to utilize blink() to pulse the relay
relay_north = LED(5, active_high=False)
relay_south = LED(6, active_high=False)

client = mqtt.Client()
client.username_pw_set(mqtt_user, password=mqtt_passwd)
client.connect(mqtt_host)

# Required to allow the state of the doors to be learned upon startup
state_north = None
state_south = None

# Report the state of the door via MQTT
def report_state(door, state):
    payload = json.dumps({"state": state})
    print(f"topic=stat/garage/{door} payload={payload}")
    client.publish(f"stat/garage/{door}", payload=payload, qos=1, retain=True)


# Trigger a relay pulse to open or close the door based on the door name and payload
def door_button(name, payload):
    if name == "north":
        state = state_north
        relay = relay_north
    elif name == "south":
        state = state_south
        relay = relay_south

    already_open = payload == "open" and state == "open"
    already_closed = payload == "close" and state == "closed"

    # If the payload matches the current state of the door, don't do anything
    if already_open or already_closed:
        print(f"The {name} door is already {state}")
    # If the payload is opposite of the current state of the door, push the button
    elif payload in ["open", "close"]:
        print(f"The {name} door relay was activated with payload: {payload}")
        relay.blink(on_time=0.5, n=1, background=True)
    # If the payload is not open or close, print a message with the invalid payload
    else:
        print(f"The {name} door relay was activated with invalid payload: {payload}")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("cmnd/garage/north")
    client.subscribe("cmnd/garage/south")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"{msg.topic} {payload}")
    if msg.topic == "cmnd/garage/north":
        door_button("north", payload)
    elif msg.topic == "cmnd/garage/south":
        door_button("south", payload)


# Determines if the door state has changed
def check_door(door, sensor, state):
    now_closed = sensor == True and (state == "open" or state == None)
    now_open = sensor == False and (state == "closed" or state == None)

    if now_closed or now_open:
        if now_closed:
            state = "closed"
        elif now_open:
            state = "open"
        report_state(door, state)
    return state


client.on_connect = on_connect
client.on_message = on_message
sleep(3)

while True:
    rc = client.loop()
    if rc != mqtt.MQTT_ERR_SUCCESS:
        try:
            # todo, don't block. Calculate time for reconnect.
            sleep(1.0)
            # todo, don't try to reconnect every failed loop iteration
            print(f"something happened, attempting to reconnect to MQTT")
            client.reconnect()
        except (socket.error, mqtt.WebsocketConnectionError):
            pass

    state_north = check_door("north", sensor_north.is_active, state_north)
    state_south = check_door("south", sensor_south.is_active, state_south)
    sleep(0.2)

