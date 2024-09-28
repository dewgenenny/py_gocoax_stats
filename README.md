# py_gocoax_stats

A Python script to fetch and monitor statistics from GoCoax MoCA devices. Originally tested with the MA2500D model, but it may work with others as well.

This script allows you to retrieve device information and MoCA network statistics, display them on the command line, and optionally publish them to an MQTT broker for integration with other tools and platforms.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Usage](#command-line-usage)
  - [Docker Usage](#docker-usage)
- [Examples](#examples)
  - [Command-Line Output](#command-line-output)
  - [MQTT Output](#mqtt-output)
- [MQTT Topic Structure](#mqtt-topic-structure)
- [Environment Variables](#environment-variables)
- [Notes](#notes)
- [License](#license)

---

## Features

- Retrieve and display device status information from GoCoax MoCA devices.
- Calculate and display PHY rates between nodes in the MoCA network.
- Publish device information and PHY rates to an MQTT broker.
- Support for multiple devices specified by IP addresses.
- Optional debugging output for troubleshooting.

---

## Requirements

- **Python 3.6** or higher.
- The following Python libraries:
  - `requests`
  - `paho-mqtt`
  - `urllib3`
- **Docker** (optional, for running the script in a container).

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/dewgenenny/py_gocoax_stats.git
cd py_gocoax_stats
```

### Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

---

## Usage

### Command-Line Usage

You can run the script directly from the command line to fetch and display stats from your GoCoax devices.

#### Syntax

```bash
python moca_info.py --username USERNAME --password PASSWORD --hosts HOST1,HOST2 [OPTIONS]
```

#### Required Arguments

- `--username`, `-u`: Username for authentication.
- `--password`, `-p`: Password for authentication.
- `--hosts`, `-H`: Comma-separated list of host IP addresses.

#### Optional Arguments

- `--mqtt-host`: MQTT broker host.
- `--mqtt-port`: MQTT broker port (default is `1883`).
- `--mqtt-user`: MQTT username.
- `--mqtt-password`: MQTT password.
- `--mqtt-base-topic`: Base MQTT topic to publish data under (default is `moca`).
- `--debug`, `-d`: Enable debugging output.

#### Example

```bash
python moca_info.py \
  --username admin \
  --password yourpassword \
  --hosts 192.168.1.100,192.168.1.101 \
  --mqtt-host mqtt.example.com \
  --mqtt-user mqttuser \
  --mqtt-password mqttpass \
  --mqtt-base-topic moca \
  --debug
```

### Docker Usage

You can run the script inside a Docker container, scheduled to execute every minute using `cron`. Configuration is provided via environment variables.

#### Build the Docker Image

```bash
docker build -t moca-monitor .
```

#### Run the Docker Container

```bash
docker run -d \
  --name moca-monitor \
  -e MOCA_USERNAME=yourusername \
  -e MOCA_PASSWORD=yourpassword \
  -e MOCA_HOSTS=192.168.1.100,192.168.1.101 \
  -e MQTT_HOST=mqtt.example.com \
  -e MQTT_PORT=1883 \
  -e MQTT_USERNAME=mqttuser \
  -e MQTT_PASSWORD=mqttpass \
  -e MQTT_BASE_TOPIC=moca \
  -e DEBUG=False \
  moca-monitor
```

#### Environment Variables

- `MOCA_USERNAME`: Username for MoCA device authentication.
- `MOCA_PASSWORD`: Password for MoCA device authentication.
- `MOCA_HOSTS`: Comma-separated list of MoCA device IP addresses.
- `MQTT_HOST`: MQTT broker host.
- `MQTT_PORT`: MQTT broker port (default is `1883`).
- `MQTT_USERNAME`: MQTT broker username.
- `MQTT_PASSWORD`: MQTT broker password.
- `MQTT_BASE_TOPIC`: Base MQTT topic to publish data under (default is `moca`).
- `DEBUG`: Set to `True` to enable debugging output.

#### View Logs

To check the output of the script running inside the Docker container:

```bash
docker logs moca-monitor
```

---

## Examples

### Command-Line Output

```plaintext
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

### MQTT Output

```
moca/192.168.xxx.xxx/status/soc_version MXL371x.1.18
moca/192.168.xxx.xxx/status/my_moca_version 2.5
moca/192.168.xxx.xxx/status/network_moca_version 2.5
moca/192.168.xxx.xxx/status/ip_address 192.168.xxx.xxx
moca/192.168.xxx.xxx/status/mac_address 94:cc:04:xx:xx:xx
moca/192.168.xxx.xxx/status/link_status Up
moca/192.168.xxx.xxx/status/lof 1150
moca/192.168.xxx.xxx/status/ethernet_tx/tx_good 2356264
moca/192.168.xxx.xxx/status/ethernet_tx/tx_bad 0
moca/192.168.xxx.xxx/status/ethernet_tx/tx_dropped 0
moca/192.168.xxx.xxx/status/ethernet_rx/rx_good 471682
moca/192.168.xxx.xxx/status/ethernet_rx/rx_bad 0
moca/192.168.xxx.xxx/status/ethernet_rx/rx_dropped 0
moca/192.168.xxx.xxx/phy_rates/gcd_rate/0 701
moca/192.168.xxx.xxx/phy_rates/gcd_rate/1 701
moca/192.168.xxx.xxx/phy_rates/from_0/to_0 701
moca/192.168.xxx.xxx/phy_rates/from_0/to_1 3656
moca/192.168.xxx.xxx/phy_rates/from_1/to_0 3656
moca/192.168.xxx.xxx/phy_rates/from_1/to_1 701
```

---

## MQTT Topic Structure

The script publishes data to MQTT under the base topic, with subtopics organized as follows:

- **Device Status Information:**

  ```
  <base_topic>/<host_ip>/status/soc_version
  <base_topic>/<host_ip>/status/my_moca_version
  <base_topic>/<host_ip>/status/network_moca_version
  <base_topic>/<host_ip>/status/ip_address
  <base_topic>/<host_ip>/status/mac_address
  <base_topic>/<host_ip>/status/link_status
  <base_topic>/<host_ip>/status/lof
  <base_topic>/<host_ip>/status/ethernet_tx/tx_good
  <base_topic>/<host_ip>/status/ethernet_tx/tx_bad
  <base_topic>/<host_ip>/status/ethernet_tx/tx_dropped
  <base_topic>/<host_ip>/status/ethernet_rx/rx_good
  <base_topic>/<host_ip>/status/ethernet_rx/rx_bad
  <base_topic>/<host_ip>/status/ethernet_rx/rx_dropped
  ```

- **PHY Rates:**

  ```
  <base_topic>/<host_ip>/phy_rates/gcd_rate/<node_id>
  <base_topic>/<host_ip>/phy_rates/from_<node_id>/to_<node_id>
  ```

**Example with Base Topic `moca` and Host IP `192.168.xxx.xxx`:**

- `moca/192.168.xxx.xxx/status/soc_version`
- `moca/192.168.xxx.xxx/phy_rates/gcd_rate/0`

---

## Environment Variables

When using Docker, configuration is provided via environment variables:

- `MOCA_USERNAME`: MoCA device username.
- `MOCA_PASSWORD`: MoCA device password.
- `MOCA_HOSTS`: Comma-separated list of MoCA device IPs.
- `MQTT_HOST`: MQTT broker host.
- `MQTT_PORT`: MQTT broker port (default `1883`).
- `MQTT_USERNAME`: MQTT broker username.
- `MQTT_PASSWORD`: MQTT broker password.
- `MQTT_BASE_TOPIC`: Base MQTT topic (default `moca`).
- `DEBUG`: Set to `True` for debugging output.

---

## Notes

- **Multiple Hosts:** The script supports multiple devices. Specify them as a comma-separated list in the `--hosts` argument or `MOCA_HOSTS` environment variable.
- **MQTT Integration:** Publishing to MQTT is optional. If `--mqtt-host` or `MQTT_HOST` is not provided, the script will only display the data on the command line.
- **Docker Time Zone:** The Docker container uses UTC by default. If you need to change the time zone, modify the Dockerfile to install `tzdata` and set the `TZ` environment variable.
- **Cron Frequency:** In the Docker setup, the script is scheduled to run every minute. You can adjust the frequency by editing the `crontab` file.
- **Security:** Ensure your credentials are stored securely. Avoid hardcoding sensitive information into scripts or images.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

Special thanks to the contributors and the community for their support and collaboration in developing this tool.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

---

## Contact

For questions or support, please open an issue on the GitHub repository.

---

**Disclaimer:** This script is provided as-is without any warranty. Use at your own risk. The author is not responsible for any damage or issues arising from the use of this script.
