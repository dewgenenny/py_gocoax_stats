# py_gocoax_stats

This is a script to fetch stats from GoCoax device (only tested with MA2500D, might work with others)

You can just specify username, password and host and it will print to the command line. If you add your MQTT details, it will also publish to MQTT :) 

usage: py_gocoax_stats.py [-h] --username USERNAME --password PASSWORD --hosts HOSTS
                          [--mqtt-host MQTT_HOST] [--mqtt-port MQTT_PORT]
                          [--mqtt-user MQTT_USER] [--mqtt-password MQTT_PASSWORD]
                          [--mqtt-base-topic MQTT_BASE_TOPIC] [--debug]

                          
