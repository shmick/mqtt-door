# mqtt-door

Use [gpiozero](https://gpiozero.readthedocs.io/en/stable/) to read the state of the magnetic reed sensors on the doors and control the doors via a relays connected to GPIO pins

Use [paho-mqtt](https://pypi.org/project/paho-mqtt/) to publish MQTT status messages and subscribe to command messages

The door contacts are [GE Overhead Panel Door Magnetic Contact](https://www.aartech.ca/2315AL-ge-overhead-panel-door-contact.html)

The relay board is found on eBay. Search for ```4-Channel Optic-Isolated Relay Module H/L Trigger 3.3V-5V Arduino / Raspberry PI```

## MQTT Status
```
topic = stat/garage/NAME
payload = {"state": "STATE"}
```
## MQTT Command
```
topic = cmnd/garage/NAME 
payload = open or close
```

## Home Assistant Sensor
```yaml
sensor garage_north:
  - platform: mqtt
    name: "Garage North"
    state_topic: "stat/garage/north"
    value_template: "{{ value_json.state }}"
```

## Home Assistant Cover
```yaml
cover garage_north:
  - platform: mqtt
    name: "Garage North"
    device_class: garage
    state_topic: "stat/garage/north"
    command_topic: "cmnd/garage/north"
    payload_open: "open"
    payload_close: "close"
    state_closed: '{"state": "closed"}'
    state_open: '{"state": "open"}'
    qos: 1
    retain: false
```