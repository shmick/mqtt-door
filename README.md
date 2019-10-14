# mqtt-door

Use [gpiozero](https://gpiozero.readthedocs.io/en/stable/) to read the state of the magnetic reed sensors on the doors and control the doors via a relays connected to GPIO pins

Use [paho-mqtt](https://pypi.org/project/paho-mqtt/) to publish MQTT status messages and subscribe to command messages

The door contacts are [GE Overhead Panel Door Magnetic Contact](https://www.aartech.ca/2315AL-ge-overhead-panel-door-contact.html)

The relay board is found on eBay. Search for ```4-Channel Optic-Isolated Relay Module H/L Trigger 3.3V-5V Arduino / Raspberry PI```