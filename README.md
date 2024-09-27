# py_gocoax_stats

This is a script to fetch stats from GoCoax device (only tested with MA2500D, might work with others)

You can just specify username, password and host and it will print to the command line. If you add your MQTT details, it will also publish to MQTT :) 

Example output:

```
Connecting to host: http://192.168.xxx.xxx

Device Status Information:
SOC Version: MXL371x.1.18
My MoCA Version: 2.5
Network MoCA Version: 2.5
IP Address: 192.168.xxx.xxx
MAC Address: 94:cc:04:xx:xx:xx
Link Status: Up
Ethernet TX:
 Tx Good: 2669586
Tx Bad: 0
Tx Dropped: 0
Ethernet RX:
 Rx Good: 499738
Rx Bad: 0
Rx Dropped: 0

Node Information:
NodeID  MAC Address     MoCA Version
0       0x94ccxxxx      0x00000025
1       0x94ccxxxx      0x00000025

PHY Rates (Mbps):
From/To 0       1
0       701     3656
1       3656    701

GCD Rates (Mbps):
NodeID  GCD Rate
0       701
1       701
```

usage: py_gocoax_stats.py [-h] --username USERNAME --password PASSWORD --hosts HOSTS
                          [--mqtt-host MQTT_HOST] [--mqtt-port MQTT_PORT]
                          [--mqtt-user MQTT_USER] [--mqtt-password MQTT_PASSWORD]
                          [--mqtt-base-topic MQTT_BASE_TOPIC] [--debug]

                          
