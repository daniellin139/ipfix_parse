### Imports ###
import time, datetime, socket, struct, sys, json, socket, collections, itertools, logging, logging.handlers, getopt
from struct import *
from defined_ports import registered_ports, other_ports
from protocol_numbers import protocol_type
# Field types, ports, etc
from field_types import ipfix_fields
#from protocol_numbers import *

#define ipfix_port
ipfix_port = 2055


###protocol parser
def mac_packed_parse(
        packed_data,  # type: "XDR Data"
        pointer,  # type: int
        field_size  # type: int
):
    """
    Parse MAC addresses passed as packed bytes that first need to be unpacked

    Args:
        packed_data (xdr): Packed XDR data
        pointer (int): Current location for unpacking
        field_size (int): Size of the packed data

    Returns:
        tuple: (MAC Address:str, MAC OUI:str)
    """
    mac_list = []
    mac_objects = struct.unpack('!%dB' % field_size, packed_data[pointer:pointer + field_size])
    for mac_item in mac_objects:
        mac_item_hex = hex(mac_item).replace('0x', '')  # Strip leading characters
        if len(mac_item_hex) == 1:
            mac_item_hex = str("0" + mac_item_hex)  # Handle leading zeros and double-0's
        mac_list.append(mac_item_hex)
    parsed_mac = (':'.join(mac_list)).upper()  # Format MAC as 00:11:22:33:44:AA
    parsed_mac_oui = (''.join(mac_list[0:3])).upper()  # MAC OUI as 001122
    return (parsed_mac, parsed_mac_oui)

def parse_ipv4(
        packed_data,  # type: struct
        pointer,  # type: int
        field_size  # type: int
    ):
    """
    Unpack an IPv4 address

    Args:
        packed_data (struct): Packed data
        pointer (int): Current unpack location
        field_size (int): Length of data to unpack

    Returns:
        str: IPv4 address
    """
    payload = socket.inet_ntoa(packed_data[pointer:pointer + field_size])
    return payload

    # Unpack IPv6
def parse_ipv6(
        packed_data,  # type: struct
        pointer,  # type: int
        field_size  # type: int
):
    """
    Unpack an IPv6 address

    Args:
        packed_data (struct): Packed data
        pointer (int): Current unpack location
        field_size (int): Length of data to unpack

    Returns:
        str: IPv4 address
    """
    payload = socket.inet_ntop(socket.AF_INET6, packed_data[pointer:pointer + field_size])
    return payload

def integer_unpack(
        packed_data,  # type: struct
        pointer,  # type: int
        field_size  # type: int
):
    """
    Unpack an Integer

    Args:
        packed_data (struct): Packed data
        pointer (int): Current unpack location
        field_size (int): Length of data to unpack

    Returns:
        str: IPv4 address
    """
    if field_size == 1:
        return unpack('!B', packed_data[pointer:pointer + field_size])[0]
    elif field_size == 2:
        return unpack('!H', packed_data[pointer:pointer + field_size])[0]
    elif field_size == 4:
        return unpack('!I', packed_data[pointer:pointer + field_size])[0]
    elif field_size == 8:
        return unpack('!Q', packed_data[pointer:pointer + field_size])[0]
    else:
        return False

def protocol_traffic_category(
        protocol_number  # type: int
):
    """
    Reconcile protocol numbers to a Category eg 89 to "Routing"

    Args:
        protocol_number (int): Traffic type eg 89 to "Routing"

    Returns:
        str: Traffic Category eg "Routing"

    """
    try:
        return protocol_type[protocol_number]["Category"]
    except (NameError, KeyError):
        return "Other"

# Tag traffic by SRC and DST port
def port_traffic_classifier(
        src_port,  # type: int
        dst_port  # type: int
):
    """
    Reconcile port numbers to services eg TCP/80 to HTTP, and services to categories eg HTTP to Web
    Args:
        src_port (int): Port number eg "443"
        dst_port (int): Port number eg "443"
    Returns:
        dict: ["Traffic":"HTTP","Traffic Category":"Web"], default value is "Other" for each.
    """
    for evaluated_port in [src_port, dst_port]:

        # Evaluate source and destination ports
        if evaluated_port in registered_ports:
            traffic = {}
            traffic["Traffic"] = registered_ports[evaluated_port]["Name"]

            if "Category" in registered_ports[evaluated_port]:
                traffic["Traffic Category"] = registered_ports[evaluated_port]["Category"]
            else:
                traffic["Traffic Category"] = "Other"
            break  # Done parsing ports

        elif evaluated_port in other_ports:
            traffic = {}
            traffic["Traffic"] = other_ports[evaluated_port]["Name"]

            if "Category" in other_ports[evaluated_port]:
                traffic["Traffic Category"] = other_ports[evaluated_port]["Category"]
            else:
                traffic["Traffic Category"] = "Other"
            break  # Done parsing ports

        else:
            pass

    try:  # Set as "Other" if not already set
        traffic
    except (NameError, KeyError):
        traffic = {}
        traffic["Traffic"] = "Other"
        traffic["Traffic Category"] = "Other"

    return traffic

###translate unix time in Milliseconds format
def millionsecond(sec):
    msec = datetime.datetime.fromtimestamp(int(sec)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
    return msec

### Get command line arguments ###
try:
    arguments = getopt.getopt(sys.argv[1:], "hl:", ["--help", "log="])

    for option_set in arguments:
        for opt, arg in option_set:

            if opt in ('-l', '--log'):  # Log level
                arg = arg.upper()  # Uppercase for matching and logging.basicConfig() format
                if arg in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
                    log_level = arg  # Use what was passed in arguments

            elif opt in ('-h', '--help'):  # Help file
                with open("./help.txt") as help_file:
                    print(help_file.read())
                sys.exit()

            else:  # No options
                pass

except Exception as argument_error:
    sys.exit("Unsupported or badly formed options, see -h for available arguments - EXITING")

### Logging level ###
# Set the logging level per https://docs.python.org/2/howto/logging.html
try:
    log_level  # Check if log level was passed in from command arguments
except NameError:
    log_level = "DEBUG"  # Use default logging level

logging.basicConfig(level=str(log_level))  # Set the logging level
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.critical('Log level set to ' + str(log_level) + " - OK")  # Show the logging level for debug


### Socket listener ###
try:
    netflow_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    netflow_sock.bind(('0.0.0.0', ipfix_port))
    logging.warning("Bound to port " + str(ipfix_port) + " - OK")
except ValueError as socket_error:
    logging.critical("Could not open or bind a socket on port " + str(ipfix_port))
    logging.critical(str(socket_error))
    sys.exit()


# IPFIX server
if __name__ == "__main__":

    flow_dic = []  # Stage the flows for the bulk API index operation

    template_list = {}  # Cache the IPFIX templates, in orderedDict to decode the data flows

    record_num = 0  # Record counter for Elasticsearch bulk upload API


    while True:  # Continually collect packets

        flow_packet_contents, sensor_address = netflow_sock.recvfrom(65565)  # Listen for packets inbound

        ### Unpack the flow packet header ###
        try:
            packet_attributes = {}  # Flow header attributes cache

            (
                packet_attributes["netflow_version"],
                packet_attributes["ipfix_flow_bytes"],
                packet_attributes["export_time"],
                packet_attributes["sequence_number"],
                packet_attributes["observation_id"]
            ) = struct.unpack('!HHLLL', flow_packet_contents[0:16])  # Unpack header

            packet_attributes["sensor"] = sensor_address[0]  # For debug purposes

            #logging.info("Unpacking header: " + str(packet_attributes))
            for x, y in packet_attributes.items():
                if x == "export_time":
                    print(x, time.ctime(int(y)))
                else:
                    print(x, y)



        # Error unpacking the header
        except Exception as flow_header_error:
            logging.warning("Failed unpacking flow header from " + str(sensor_address[0]) + " - FAIL")
            logging.warning(flow_header_error)
            continue

        ### Check IPFIX version ###
        if int(packet_attributes["netflow_version"]) != 10:
            logging.warning("Received a non-IPFIX packet from " + str(sensor_address[0]) + " - DROPPING")
            continue

        byte_position = 16  # Position after the standard protocol header

        ### Iterate through total flows in the packet ###
        #
        # Can be any combination of templates and data flows, any lengths
        while True:

            ### Unpack the flow set ID and the length ###
            #
            # Determine if it's a template set or a data set and the size
            try:
                logging.info("Unpacking ID and length at byte position " + str(byte_position))
                (flow_set_id, flow_set_length) = struct.unpack('!HH',
                                                               flow_packet_contents[byte_position:byte_position + 4])
                logging.info("Flow ID, Length " + str((flow_set_id, flow_set_length)))
            except Exception as id_unpack_error:
                logging.info("Out of bytes to unpack, breaking")
                break  # Done with the packet

            # Advance past the initial header of ID and length
            byte_position += 4

            ### Parse sets based on Set ID ###
            # ID 0 and 1 are not used
            # ID 2 is a Template
            # ID 3 is an Options Template
            # IDs > 255 are flow data

            # IPFIX template set (ID 2)
            if flow_set_id == 2:
                template_position = byte_position
                final_template_position = (byte_position + flow_set_length) - 4

                # Cache for the following templates
                template_cache = {}

                while template_position < final_template_position:
                    logging.info("Unpacking template set at " + str(template_position))
                    (template_id, template_id_length) = struct.unpack('!HH', flow_packet_contents[
                                                                             template_position:template_position + 4])
                    logging.info("Found (ID, Elements) -- " + str((template_id, template_id_length)))

                    template_position += 4  # Advance

                    # Template for flow data set
                    if template_id > 255:

                        # Produce unique hash to identify unique template ID and sensor
                        hashed_id = hash(str(sensor_address[0]) + str(template_id))

                        # Cache to upload to template store
                        template_cache[hashed_id] = {}
                        template_cache[hashed_id]["Sensor"] = str(sensor_address[0])
                        template_cache[hashed_id]["Template ID"] = template_id
                        template_cache[hashed_id]["Length"] = template_id_length
                        template_cache[hashed_id]["Definitions"] = collections.OrderedDict()  # ORDER MATTERS

                        # Iterate through template lines
                        for _ in range(0, template_id_length):
                            # Unpack template element number and length
                            (template_element, template_element_length) = struct.unpack('!HH', flow_packet_contents[
                                                                                               template_position:template_position + 4])

                            # Cache each Element and its Length
                            template_cache[hashed_id]["Definitions"][template_element] = template_element_length

                            # Advance
                            template_position += 4

                    template_list.update(template_cache)  # Add template to the template cache
                    #logging.debug(str(template_list))
                    #for x, y in template_list.items():
                    #    #print(x, y)
                    #    for a, b in y.items():
                    #        #print(a, b)
                    #        if a == "Definitions":
                    #            for x1, y1 in b.items():
                    #                print(type(y1))
                    #                print(x1, y1)
                    #        elseÔºö
                    #            print(a, b)

                    logging.info("Template " + str(template_id) + " parsed successfully")

                logging.info("Finished parsing templates at byte " + str(template_position) + " of " + str(
                    final_template_position))

                byte_position = (flow_set_length + byte_position) - 4  # Advance to the end of the flow

            # IPFIX options template set (ID 3)
            elif flow_set_id == 3:
                logging.info("Unpacking Options Template set at " + str(byte_position))
                logging.warning("Received IPFIX Options Template, not currently supported - SKIPPING")
                byte_position = (flow_set_length + byte_position) - 4
                logging.info("Finished Options Template set at " + str(byte_position))
                break  # Code to parse the Options Template will go here eventually

            # Received an IPFIX flow data set, corresponding with a template
            elif flow_set_id > 255:

                # Compute the template hash ID
                hashed_id = hash(str(sensor_address[0]) + str(flow_set_id))

                # Check if there is a template
                if hashed_id in template_list.keys():

                    logging.info("Parsing data flow " + str(flow_set_id) + " at byte " + str(byte_position))

                    now = datetime.datetime.utcnow()  # Get the current UTC time for the flows
                    data_position = byte_position  # Temporary counter

                    # Iterate through flow bytes until we run out
                    while data_position + 4 <= (flow_set_length + (byte_position - 4)):

                        logging.info(
                            "Parsing flow " + str(flow_set_id) + " at " + str(data_position) + ", sequence " + str(
                                packet_attributes["sequence_number"]))

                        # Cache the flow data, to be appended to flow_dic[]
                        flow_index = {
                            "_index": str("flow-" + now.strftime("%Y-%m-%d")),
                            "_type": "Flow",
                            "_source": {
                                "Flow Type": "IPFIX",
                                "Sensor": sensor_address[0],
                                "Sequence": packet_attributes["sequence_number"],
                                "Observation Domain": str(packet_attributes["observation_id"]),
                                "Time": now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z",
                            }
                        }
                        # Iterate through template elements
                        for template_key, field_size in template_list[hashed_id]["Definitions"].items():

                            # Integer type field, parse further
                            if ipfix_fields[template_key]["Type"] == "Integer":

                                # Unpack the integer
                                flow_payload = integer_unpack(flow_packet_contents, data_position, field_size)

                                # IANA protocol number
                                if template_key == 4:
                                    flow_index["_source"]['Protocol Number'] = flow_payload

                                # Do the special calculations for ICMP Code and Type (% operator)
                                elif template_key in [32, 139]:
                                    flow_index["_source"]['ICMP Type'] = int(flow_payload) // 256
                                    flow_index["_source"]['ICMP Code'] = int(flow_payload) % 256

                                # Not a specially parsed integer field, just ignore and log the payload
                                else:
                                    pass

                                # Apply friendly Options name if available
                                #if "Options" in ipfix_fields[template_key]:
                                #    flow_index["_source"][ipfix_fields[template_key]["Index ID"]] = \
                                #    ipfix_fields[template_key]['Options'][int(flow_payload)]

                                #    # Advance the position for the field
                                #    data_position += field_size
                                #    continue  # Skip the rest, it's fully parsed

                                # No "Options" specified for this field type
                                #else:
                                #    pass

                            # IPv4 Address
                            elif ipfix_fields[template_key]["Type"] == "IPv4":
                                flow_payload = parse_ipv4(flow_packet_contents, data_position, field_size)
                                flow_index["_source"]["IP Protocol Version"] = 4

                            # IPv6 Address
                            elif ipfix_fields[template_key]["Type"] == "IPv6":
                                flow_payload = parse_ipv6(flow_packet_contents, data_position, field_size)
                                flow_index["_source"]["IP Protocol Version"] = 6

                                # MAC Address
                            elif ipfix_fields[template_key]["Type"] == "MAC":

                                # Parse MAC
                                parsed_mac = mac_packed_parse(flow_packet_contents, data_position, field_size)
                                flow_payload = parsed_mac[0]  # Parsed MAC address

                            # Check if we've been passed a "Vendor Proprietary" field, and if so log it and skip it
                            elif ipfix_fields[template_key]["Type"] == "Vendor Proprietary":
                                logging.info(
                                    "Received vendor proprietary field, " +
                                    str(template_key) +
                                    ", in " +
                                    str(flow_set_id) +
                                    " from " +
                                    str(sensor_address[0])
                                )

                            # Something we haven't accounted for yet
                            else:
                                try:
                                    flow_payload = struct.unpack('!%dc' % field_size, flow_packet_contents[data_position:(data_position + field_size)])
                                except Exception as unpack_error:
                                    logging.debug(
                                        "Error unpacking generic field number " +
                                        str(ipfix_fields[field_definition]) +
                                        ", error messages: " +
                                        str(unpack_error)
                                    )

                            # Add the friendly Index ID and value (flow_payload) to flow_index
                            flow_index["_source"][ipfix_fields[int(template_key)]["Index ID"]] = flow_payload

                            # Move the byte position the number of bytes we just parsed
                            data_position += field_size

                        ### Traffic and Traffic Category tagging ###
                        #
                        # Transport protocols eg TCP, UDP, etc
                        if int(flow_index["_source"]['Protocol Number']) in (6, 17, 33, 132):
                            traffic_tags = port_traffic_classifier(
                                flow_index["_source"]["Source Port"], flow_index["_source"]["Destination Port"])
                            flow_index["_source"]["Traffic"] = traffic_tags["Traffic"]
                            flow_index["_source"]["Traffic Category"] = traffic_tags["Traffic Category"]

                        # Non-transport protocols eg OSPF, VRRP, etc
                        else:
                            try:
                                flow_index["_source"][
                                    "Traffic Category"] = protocol_traffic_category(
                                    flow_index["_source"]['Protocol Number'])
                            except:
                                flow_index["_source"]["Traffic Category"] = "Uncategorized"

                        #Append this single flow to the flow_dic[] for bulk upload
                        #logging.debug(str(flow_index))
                        for key, val in flow_index["_source"].items():
                            if str(key) == "Flow Start Milliseconds" or str(key) == "Flow End Milliseconds":
                                logging.debug(str(key) + ":" + millionsecond(val))
                            else:
                                logging.debug(str(key) + ":" + str(val))
                        #flow_dic.append(flow_index)
                        #logging.debug(str(flow_dic))

                        logging.info(
                            "Finished sequence " + str(packet_attributes["sequence_number"]) + " at byte " + str(
                                data_position))

                        record_num += 1  # Increment record counter
                        packet_attributes["sequence_number"] += 1  # Increment sequence number, per IPFIX standard

                # No template, drop the flow per the standard and advanced the byte position
                else:
                    byte_position += flow_set_length
                    logging.warning(
                        "Waiting on template " +
                        str(flow_set_id) +
                        " from " +
                        str(sensor_address[0]) +
                        ", sequence " +
                        str(packet_attributes["sequence_number"]) +
                        " - DROPPING"
                    )
                    break

                byte_position = (flow_set_length + byte_position) - 4  # Advance to the end of the flow
                logging.info("Ending data set at " + str(byte_position))

            # Received a flow set ID we haven't accounted for
            else:
                logging.warning("Unknown flow ID " + str(flow_set_id) + " from " + str(sensor_address[0]))
                break  # Bail out