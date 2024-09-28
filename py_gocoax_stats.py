import requests
import json
import argparse
import paho.mqtt.client as mqtt  # Import the MQTT library
from requests.auth import HTTPDigestAuth  # Import if Digest Authentication is needed

# Suppress SSL warnings if the device uses a self-signed certificate
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the endpoints globally
endpoints = {
    'devStatus': '/devStatus.html',   # To retrieve the CSRF token
    'phyRates': '/phyRates.html',     # For the referer in the headers
    'localInfo': '/ms/0/0x15',
    'netInfo': '/ms/0/0x16',
    'fmrInfo': '/ms/0/0x1D',
    'miscphyinfo': '/ms/0/0x24',
    'macInfo': '/ms/1/0x103/GET',
    'frameInfo': '/ms/0/0x14',
    'lof': '/ms/0/0x1003/GET',
    'ipAddr': '/ms/1/0x20b/GET',
    'ChipID': '/ms/1/0x303/GET',
    'gpio': '/ms/1/0xb17',
    'miscm25phyinfo': '/ms/0/0x7f',
}

# Function to get CSRF token from cookies
def get_csrf_token(session):
    return session.cookies.get('csrf_token')

# Function to perform POST requests with CSRF token and proper headers
def post_data(session, base_url, action_url, payload_dict=None, referer=None, payload_format='json', debug=False):
    url = base_url + action_url
    csrf_token = get_csrf_token(session)
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Connection': 'keep-alive',
        'Origin': base_url,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    if referer:
        headers['Referer'] = base_url + referer
    else:
        headers['Referer'] = base_url + endpoints['devStatus']

    if payload_format == 'json':
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        headers['Content-Type'] = 'application/json'
        if payload_dict is None:
            payload_dict = {"data": []}
        payload_str = json.dumps(payload_dict)
    elif payload_format == 'form':
        headers['Accept'] = 'text/html, */*'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if payload_dict is None:
            payload_dict = {}
        payload_str = payload_dict
    else:
        raise ValueError("Invalid payload_format specified.")

    if csrf_token:
        headers['X-CSRF-TOKEN'] = csrf_token
        headers['Cookie'] = f'csrf_token={csrf_token}'

    # Debugging statements
    if debug:
        print(f"POST URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload_str}\n")

    response = session.post(url, data=payload_str, headers=headers, verify=False)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        if debug:
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text}\n")
        raise

# Function to perform GET requests
def get_data(session, base_url, action_url, referer=None, debug=False):
    url = base_url + action_url
    csrf_token = get_csrf_token(session)
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html, */*',
        'Connection': 'keep-alive',
    }
    if referer:
        headers['Referer'] = base_url + referer
    if csrf_token:
        headers['X-CSRF-TOKEN'] = csrf_token
        headers['Cookie'] = f'csrf_token={csrf_token}'

    if debug:
        print(f"GET URL: {url}")
        print(f"Headers: {headers}\n")

    response = session.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response

# Function to retrieve device information
def retrieve_device_info(session, base_url, debug=False):
    # Access devStatus.html to obtain the CSRF token
    dev_status_url = base_url + endpoints['devStatus']
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html, */*',
        'Connection': 'keep-alive',
    }

    if debug:
        print(f"Accessing devStatus.html at {dev_status_url}")

    response = session.get(dev_status_url, headers=headers, verify=False)
    response.raise_for_status()
    csrf_token = get_csrf_token(session)
    if not csrf_token:
        print("Failed to retrieve CSRF token.")
        return None

    device_info = {}

    # Step 1: Get localInfo
    local_info = post_data(session, base_url, endpoints['localInfo'], debug=debug)
    device_info['localInfo'] = local_info['data']
    myNodeId = int(device_info['localInfo'][0], 16)

    # Step 2: Get miscphyinfo
    miscphyinfo = post_data(session, base_url, endpoints['miscphyinfo'], debug=debug)
    device_info['miscphyinfo'] = miscphyinfo['data']

    # Step 3: Get netInfo
    payload_dict = {"data": [myNodeId]}
    net_info = post_data(session, base_url, endpoints['netInfo'], payload_dict=payload_dict, debug=debug)
    device_info['netInfo'] = net_info['data']

    # Step 4: Get macInfo
    mac_info = post_data(session, base_url, endpoints['macInfo'], payload_dict={"data": [myNodeId]}, debug=debug)
    device_info['macInfo'] = mac_info['data']

    # Step 5: Get frameInfo
    frame_info = post_data(session, base_url, endpoints['frameInfo'], payload_dict={"data": [0]}, debug=debug)
    device_info['frameInfo'] = frame_info['data']

    # Step 6: Get lof
    lof = post_data(session, base_url, endpoints['lof'], debug=debug)
    device_info['lof'] = lof['data']

    # Step 7: Get ipAddr
    ip_addr = post_data(session, base_url, endpoints['ipAddr'], debug=debug)
    device_info['ipAddr'] = ip_addr['data']

    # Step 8: Get ChipID
    chip_id = post_data(session, base_url, endpoints['ChipID'], debug=debug)
    device_info['chipId'] = chip_id['data']

    # Step 9: Get gpio
    gpio = post_data(session, base_url, endpoints['gpio'], payload_dict={"data": [0]}, debug=debug)
    device_info['gpio'] = gpio['data']

    # Step 10: Get miscm25phyinfo
    miscm25phyinfo = post_data(session, base_url, endpoints['miscm25phyinfo'], debug=debug)
    device_info['miscm25phyinfo'] = miscm25phyinfo['data']

    return device_info

# Helper functions
def byte2ascii(hex_str):
    # Convert hex string to ASCII characters
    try:
        bytes_obj = bytes.fromhex(hex_str)
        ascii_str = ''
        for b in bytes_obj:
            if 0 < b < 0x80:
                ascii_str += chr(b)
            else:
                return ''
        return ascii_str
    except ValueError:
        return ''

def hex2mac(hi, lo):
    # Convert hi and lo integers to MAC address string
    mac_parts = [
        f"{(hi >> 24) & 0xFF:02x}",
        f"{(hi >> 16) & 0xFF:02x}",
        f"{(hi >> 8) & 0xFF:02x}",
        f"{hi & 0xFF:02x}",
        f"{(lo >> 24) & 0xFF:02x}",
        f"{(lo >> 16) & 0xFF:02x}",
    ]
    return ':'.join(mac_parts)

# Function to process and display the device information
def display_device_info(device_info):
    # Extract variables similar to the JavaScript code
    local_info = device_info['localInfo']
    miscphyinfo = device_info['miscphyinfo']
    net_info = device_info['netInfo']
    mac_info = device_info['macInfo']
    frame_info = device_info['frameInfo']
    lof = device_info['lof']
    ip_addr = device_info['ipAddr']
    chip_id = device_info['chipId']
    gpio = device_info['gpio']
    miscm25phyinfo = device_info['miscm25phyinfo']

    # Process the data as in the JavaScript code
    nwMocaVer = int(local_info[11], 16)
    nwMocaVerVal = f"{(nwMocaVer >> 4) & 0xF}.{nwMocaVer & 0xF}"

    linkStatus = int(local_info[5], 16)
    linkStatusVal = "Up" if linkStatus else "Down"

    socVersion = ''
    i = 0
    while True:
        if 21 + i >= len(local_info):
            break
        val = local_info[21 + i][2:10]
        retVal = byte2ascii(val)
        if not retVal:
            break
        socVersion += retVal
        i += 1

    # Determine chip name
    chipArray = ["MXL370x", "MXL371x", "UNKNOWN"]
    chipId = int(chip_id[0], 16)  # Specify base 16
    chipIdIndex = chipId - 0x15
    if chipIdIndex >= len(chipArray):
        chipIdIndex = len(chipArray) - 1
    chipName = chipArray[chipIdIndex]
    socVersionVal = f"{chipName}.{socVersion}"

    # MAC Address
    hi = int(mac_info[0], 16)  # Specify base 16
    lo = int(mac_info[1], 16)  # Specify base 16
    macAddressVal = hex2mac(hi, lo)

    # My MoCA Version
    myMocaVer = int(net_info[4], 16)
    myMocaVerVal = f"{(myMocaVer >> 4) & 0xF}.{myMocaVer & 0xF}"

    # Ethernet TX/RX values
    txgood = ((int(frame_info[12], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[13], 16)
    txbad = ((int(frame_info[30], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[31], 16)
    txdropped = ((int(frame_info[48], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[49], 16)
    ethTxVal = f"Tx Good: {txgood}\n Tx Bad: {txbad}\n Tx Dropped: {txdropped}"

    rxgood = ((int(frame_info[66], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[67], 16)
    rxbad = ((int(frame_info[84], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[85], 16)
    rxdropped = ((int(frame_info[102], 16) & 0xFFFFFFFF) * 4294967296) + int(frame_info[103], 16)
    ethRxVal = f"Rx Good: {rxgood}\n Rx Bad: {rxbad}\n Rx Dropped: {rxdropped}"

    # IP Address
    ipAddr = int(ip_addr[0], 16)
    ipAddrVal = f"{(ipAddr >> 24) & 0xFF}.{(ipAddr >> 16) & 0xFF}.{(ipAddr >> 8) & 0xFF}.{ipAddr & 0xFF}"

    # LOF Value
    lofVal = int(lof[0], 16)

    # Display the information
    print("\nDevice Status Information:")
    print("SOC Version:", socVersionVal)
    print("My MoCA Version:", myMocaVerVal)
    print("Network MoCA Version:", nwMocaVerVal)
    print("IP Address:", ipAddrVal)
    print("MAC Address:", macAddressVal)
    print("Link Status:", linkStatusVal)
    print("Ethernet TX:\n", ethTxVal)
    print("Ethernet RX:\n", ethRxVal)
    # Add more print statements as needed for other values

    # Return the processed information as a dictionary for MQTT publishing
    return {
        "soc_version": socVersionVal,
        "my_moca_version": myMocaVerVal,
        "network_moca_version": nwMocaVerVal,
        "ip_address": ipAddrVal,
        "mac_address": macAddressVal,
        "link_status": linkStatusVal,
        "ethernet_tx": {
            "tx_good": txgood,
            "tx_bad": txbad,
            "tx_dropped": txdropped,
        },
        "ethernet_rx": {
            "rx_good": rxgood,
            "rx_bad": rxbad,
            "rx_dropped": rxdropped,
        },
        "lof": lofVal,
    }

# Include the get_phy_rates function, adjusted to use 'session', 'base_url', and 'debug'
def get_phy_rates(session, base_url, debug=False):
    # Define constants and variables
    MAX_NUM_NODES = 16
    LDPC_LEN_100MHZ = 3900
    LDPC_LEN_50MHZ = 1200
    FFT_LEN_100MHZ = 512
    FFT_LEN_50MHZ = 256

    # Step 0: Access phyRates.html to obtain the CSRF token
    phy_rates_url = base_url + endpoints['phyRates']
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html, */*',
        'Connection': 'keep-alive',
    }

    if debug:
        print(f"Accessing phyRates.html at {phy_rates_url}")

    response = session.get(phy_rates_url, headers=headers, verify=False)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error accessing phyRates.html: {err}")
        print("Failed to retrieve CSRF token. Please check your credentials and device connection.")
        return None

    csrf_token = get_csrf_token(session)
    if not csrf_token:
        print("Failed to retrieve CSRF token.")
        return None

    # Initialize data structures
    rateNper = [[0]*MAX_NUM_NODES for _ in range(MAX_NUM_NODES)]
    rateVlper = [[0]*MAX_NUM_NODES for _ in range(MAX_NUM_NODES)]
    rateGcd = [0]*MAX_NUM_NODES
    netInfo = [None]*MAX_NUM_NODES
    fmrInfo = [None]*MAX_NUM_NODES
    nodeId = []

    # Step 1: Get localInfo
    local_info_response = post_data(session, base_url, endpoints['localInfo'], debug=debug)
    LocalInfo = local_info_response['data']
    myNodeID = int(LocalInfo[0], 16)
    mocaNetVer = int(LocalInfo[11], 16)
    nodeBitMask = int(LocalInfo[12], 16)
    ncNodeID = int(LocalInfo[1], 16) & 0xFF

    # Step 2: Get netInfo for each node
    for node_id in range(MAX_NUM_NODES):
        currNodeMask = 1 << node_id
        if nodeBitMask & currNodeMask:
            payload_dict = {"data": [int(node_id)]}
            net_info_response = post_data(session, base_url, endpoints['netInfo'], payload_dict=payload_dict, debug=debug)
            netInfo[node_id] = net_info_response['data']
            nodeId.append(node_id)
        else:
            netInfo[node_id] = None

    # Get NC's MoCA version
    ncMocaVer = int(netInfo[ncNodeID][4], 16) & 0xFF

    # Step 3: Get fmrInfo for each node
    for node_id in nodeId:
        # Node's MoCA version
        nodeMocaVer = int(netInfo[node_id][4], 16) & 0xFF
        mocaVer = min(ncMocaVer, nodeMocaVer)
        if mocaVer < 0x20:
            finalVer = 1
        else:
            finalVer = 2
        currNodeMask = 1 << node_id

        # Prepare payload as JSON with 'data' as a list of two values
        payload_dict = {
            "data": [int(currNodeMask), finalVer]
        }

        fmr_info_response = post_data(
            session, base_url,
            endpoints['fmrInfo'],
            payload_dict=payload_dict,
            payload_format='json',
            debug=debug
        )
        fmrInfo[node_id] = fmr_info_response['data']

    # Step 4: Calculate PHY rates
    numNode = len(nodeId)
    for id_index, id in enumerate(nodeId):
        entryNodePayloadVer = min(int(netInfo[id][4], 16) & 0xFF, ncMocaVer)
        readIndx = 10
        alignmentFlag = True
        rateGcd[id_index] = 0
        mocaNodeVer = int(netInfo[id][4], 16) & 0xFF

        for jd_index, jd in enumerate(nodeId):
            # Determine fmrPayloadVer
            node_jd_mocaNodeVer = int(netInfo[jd][4], 16) & 0xFF
            if ncMocaVer < 0x20:
                fmrPayloadVer = min(entryNodePayloadVer, node_jd_mocaNodeVer)
            else:
                fmrPayloadVer = mocaNodeVer

            # Parse fmrInfo data
            fmr_data = fmrInfo[id]
            try:
                if fmrPayloadVer in (0x20, 0x25):
                    # MoCA 2.x
                    if alignmentFlag:
                        val1 = int(fmr_data[readIndx], 16)
                        gapNper = (val1 >> 24) & 0xFF
                        gapVLper = (val1 >> 16) & 0xFF
                        ofdmbNper = val1 & 0xFFFF
                        val2 = int(fmr_data[readIndx+1], 16)
                        ofdmbVLper = (val2 >> 16) & 0xFFFF
                        readIndx += 1
                    else:
                        val1 = int(fmr_data[readIndx], 16)
                        gapNper = (val1 >> 8) & 0xFF
                        gapVLper = val1 & 0xFF
                        val2 = int(fmr_data[readIndx+1], 16)
                        ofdmbNper = (val2 >> 16) & 0xFFFF
                        ofdmbVLper = val2 & 0xFFFF
                        readIndx += 2
                else:
                    # MoCA 1.x
                    gapVLper = 0
                    ofdmbVLper = 0
                    val = int(fmr_data[readIndx], 16)
                    if alignmentFlag:
                        gapNper = (val & 0xF8000000) >> 27
                        ofdmbNper = (val & 0x07FF0000) >> 16
                    else:
                        gapNper = (val & 0x0000F800) >> 11
                        ofdmbNper = val & 0x000007FF
                        readIndx += 1
                alignmentFlag = not alignmentFlag

                # Calculate PHY rates
                if gapVLper == 0:
                    rateVlper[id_index][jd_index] = 0
                else:
                    rateVlper[id_index][jd_index] = (LDPC_LEN_100MHZ * ofdmbVLper) // ((FFT_LEN_100MHZ + ((gapVLper + 10) * 2)) * 46)

                if gapNper == 0:
                    rateNper[id_index][jd_index] = 0
                elif gapVLper == 0 and fmrPayloadVer == 0x20:
                    rateNper[id_index][jd_index] = (LDPC_LEN_50MHZ * ofdmbNper) // ((FFT_LEN_50MHZ + (gapNper * 2 + 10)) * 26)
                else:
                    rateNper[id_index][jd_index] = (LDPC_LEN_100MHZ * ofdmbNper) // ((FFT_LEN_100MHZ + ((gapNper + 10) * 2)) * 46)

                # Calculate GCD
                if id == jd:
                    if (mocaNodeVer & 0xF0) == 0x10:
                        # MoCA 1.x
                        gapGcd = gapNper
                        ofdmbGcd = ofdmbNper
                        rateGcd[id_index] = (LDPC_LEN_50MHZ * ofdmbGcd) // ((FFT_LEN_50MHZ + (gapGcd * 2 + 10)) * 26)
                    elif (mocaNodeVer & 0xF0) == 0x20:
                        # MoCA 2.x
                        gapGcd = gapNper
                        ofdmbGcd = ofdmbNper
                        rateGcd[id_index] = (LDPC_LEN_100MHZ * ofdmbGcd) // ((FFT_LEN_100MHZ + ((gapGcd + 10) * 2)) * 46)
            except Exception as e:
                print(f"Error parsing FMR data for node {id}: {e}")
                rateNper[id_index][jd_index] = 0
                rateVlper[id_index][jd_index] = 0

    # Step 5: Display the PHY rates and other statistics

    # Display Node Information
    print("\nNode Information:")
    print("NodeID\tMAC Address\tMoCA Version")
    for node_id in nodeId:
        mac_address = netInfo[node_id][0]
        moca_version = netInfo[node_id][4]
        print(f"{node_id}\t{mac_address}\t{moca_version}")

    # Display PHY Rates (Mbps)
    print("\nPHY Rates (Mbps):")
    header = ["From/To"] + [str(nid) for nid in nodeId]
    print("\t".join(header))
    for i, id_from in enumerate(nodeId):
        row = [str(id_from)]
        for j, id_to in enumerate(nodeId):
            rate = rateNper[i][j]  # Use rateVlper[i][j] if needed
            row.append(str(rate))
        print("\t".join(row))

    # Display GCD Rates
    print("\nGCD Rates (Mbps):")
    print("NodeID\tGCD Rate")
    for i, node_id in enumerate(nodeId):
        print(f"{node_id}\t{rateGcd[i]}")

    # Prepare data for MQTT publishing
    phy_rates_data = {
        "nodes": nodeId,
        "rates": rateNper,
        "gcd_rates": rateGcd,
    }

    return phy_rates_data

# Function to publish data to MQTT
def publish_to_mqtt(mqtt_client, base_topic, host_ip, device_info, phy_rates_data, debug=False):
    # Device status information
    status_topic = f"{base_topic}/{host_ip}/status"
    mqtt_client.publish(f"{status_topic}/soc_version", device_info["soc_version"])
    mqtt_client.publish(f"{status_topic}/my_moca_version", device_info["my_moca_version"])
    mqtt_client.publish(f"{status_topic}/network_moca_version", device_info["network_moca_version"])
    mqtt_client.publish(f"{status_topic}/ip_address", device_info["ip_address"])
    mqtt_client.publish(f"{status_topic}/mac_address", device_info["mac_address"])
    mqtt_client.publish(f"{status_topic}/link_status", device_info["link_status"])
    mqtt_client.publish(f"{status_topic}/lof", device_info["lof"])

    # Ethernet TX
    eth_tx = device_info["ethernet_tx"]
    mqtt_client.publish(f"{status_topic}/ethernet_tx/tx_good", eth_tx["tx_good"])
    mqtt_client.publish(f"{status_topic}/ethernet_tx/tx_bad", eth_tx["tx_bad"])
    mqtt_client.publish(f"{status_topic}/ethernet_tx/tx_dropped", eth_tx["tx_dropped"])

    # Ethernet RX
    eth_rx = device_info["ethernet_rx"]
    mqtt_client.publish(f"{status_topic}/ethernet_rx/rx_good", eth_rx["rx_good"])
    mqtt_client.publish(f"{status_topic}/ethernet_rx/rx_bad", eth_rx["rx_bad"])
    mqtt_client.publish(f"{status_topic}/ethernet_rx/rx_dropped", eth_rx["rx_dropped"])

    # PHY Rates
    rates_topic = f"{base_topic}/{host_ip}/phy_rates"
    nodes = phy_rates_data["nodes"]
    rates = phy_rates_data["rates"]
    gcd_rates = phy_rates_data["gcd_rates"]

    # Publish GCD Rates
    for i, node_id in enumerate(nodes):
        mqtt_client.publish(f"{rates_topic}/gcd_rate/{node_id}", gcd_rates[i])

    # Publish Rates between nodes
    for i, id_from in enumerate(nodes):
        for j, id_to in enumerate(nodes):
            rate = rates[i][j]
            mqtt_client.publish(f"{rates_topic}/from_{id_from}/to_{id_to}", rate)

    if debug:
        print(f"Published data to MQTT under base topic '{base_topic}/{host_ip}'.")

# Main execution
if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Retrieve MoCA device information and publish to MQTT.')
    parser.add_argument('--username', '-u', type=str, required=True, help='Username for authentication')
    parser.add_argument('--password', '-p', type=str, required=True, help='Password for authentication')
    parser.add_argument('--hosts', '-H', type=str, required=True, help='Comma-separated list of host IP addresses')
    parser.add_argument('--mqtt-host', type=str, required=False, help='MQTT broker host')
    parser.add_argument('--mqtt-port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    parser.add_argument('--mqtt-user', type=str, required=False, help='MQTT username')
    parser.add_argument('--mqtt-password', type=str, required=False, help='MQTT password')
    parser.add_argument('--mqtt-base-topic', type=str, default='moca', help='Base MQTT topic (default: "moca")')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debugging output')

    args = parser.parse_args()

    username = args.username
    password = args.password
    host_list = args.hosts.split(',')
    debug = args.debug

    # MQTT configuration
    mqtt_host = args.mqtt_host
    mqtt_port = args.mqtt_port
    mqtt_user = args.mqtt_user
    mqtt_password = args.mqtt_password
    mqtt_base_topic = args.mqtt_base_topic

    # Initialize MQTT client if MQTT host is provided
    mqtt_client = None
    if mqtt_host:
        mqtt_client = mqtt.Client()
        if mqtt_user and mqtt_password:
            mqtt_client.username_pw_set(mqtt_user, mqtt_password)
        try:
            mqtt_client.connect(mqtt_host, mqtt_port)
            if debug:
                print(f"Connected to MQTT broker at {mqtt_host}:{mqtt_port}")
            # Start the MQTT network loop
            mqtt_client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            mqtt_client = None

    # Iterate over each host
    for host in host_list:
        base_url = f'http://{host.strip()}'
        print(f"\nConnecting to host: {base_url}")

        # Create a new session for each host
        session = requests.Session()
        session.auth = (username, password)  # For Basic Authentication

        try:
            # Retrieve device information
            device_info = retrieve_device_info(session, base_url, debug=debug)
            if device_info:
                processed_info = display_device_info(device_info)
            else:
                print("Failed to retrieve device information.")
                continue

            # Now retrieve PHY rates
            phy_rates_data = get_phy_rates(session, base_url, debug=debug)
            if not phy_rates_data:
                print("Failed to retrieve PHY rates.")
                continue

            # Publish data to MQTT if client is available
            if mqtt_client:
                publish_to_mqtt(mqtt_client, mqtt_base_topic, host.strip(), processed_info, phy_rates_data, debug=debug)
                # Optionally, process network events to ensure messages are sent
                mqtt_client.loop()

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            print("Failed to retrieve data. Please check your credentials and device connection.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Failed to retrieve data. Please check your credentials and device connection.")

    # Disconnect MQTT client
    if mqtt_client:
        # Stop the MQTT network loop
        mqtt_client.loop_stop()
        mqtt_client.disconnect()