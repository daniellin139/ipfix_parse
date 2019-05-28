# ipfix_parser
# python3 ipfix_parser   //command to start parser
# 
# Support ipfix(version10) only, tested with the following config on Juniper MX router for both IPv4 and IPv6.
#set chassis fpc 0 sampling-instance instance-1
#set chassis fpc 0 inline-services flow-table-size ipv4-flow-table-size 8
#set chassis fpc 0 inline-services flow-table-size ipv6-flow-table-size 8
#set services flow-monitoring version-ipfix template template-v4 flow-active-timeout 10
#set services flow-monitoring version-ipfix template template-v4 flow-inactive-timeout 10
#set services flow-monitoring version-ipfix template template-v4 template-refresh-rate seconds 10
#set services flow-monitoring version-ipfix template template-v4 ipv4-template
#set services flow-monitoring version-ipfix template template-v6 flow-active-timeout 10
#set services flow-monitoring version-ipfix template template-v6 flow-inactive-timeout 10
#set services flow-monitoring version-ipfix template template-v6 template-refresh-rate seconds 30
#set services flow-monitoring version-ipfix template template-v6 ipv6-template
#set forwarding-options sampling instance instance-1 input rate 1
#set forwarding-options sampling instance instance-1 family inet output flow-server 200.0.0.2 port 2055
#set forwarding-options sampling instance instance-1 family inet output flow-server 200.0.0.2 version-ipfix template template-v4
#set forwarding-options sampling instance instance-1 family inet output inline-jflow source-address 200.0.0.1
#set forwarding-options sampling instance instance-1 family inet output inline-jflow flow-export-rate 10
#set forwarding-options sampling instance instance-1 family inet6 output flow-server 200.0.0.2 port 2055
#set forwarding-options sampling instance instance-1 family inet6 output flow-server 200.0.0.2 version-ipfix template template-v6
#set forwarding-options sampling instance instance-1 family inet6 output inline-jflow source-address 200.0.0.1
#set forwarding-options sampling instance instance-1 family inet6 output inline-jflow flow-export-rate 10
#set firewall family inet filter ipv4-sample term 1 then sample
#set firewall family inet filter ipv4-sample term 1 then accept
#set firewall family inet6 filter ipv6-smaple term 1 then sample
#set firewall family inet6 filter ipv6-smaple term 1 then accept

#exmaple data from /var/log/ipfix.log:
#IPv6 traffic
2019-05-28 18:06:49,558 - root       - DEBUG    - Flow Type:IPFIX
2019-05-28 18:06:49,558 - root       - DEBUG    - Sensor:200.0.0.1
2019-05-28 18:06:49,558 - root       - DEBUG    - Sequence:6668
2019-05-28 18:06:49,558 - root       - DEBUG    - Observation Domain:589824
2019-05-28 18:06:49,558 - root       - DEBUG    - Time:2019-05-28T18:06:49.558Z
2019-05-28 18:06:49,558 - root       - DEBUG    - IP Protocol Version:6
2019-05-28 18:06:49,559 - root       - DEBUG    - IPv6 Source:2001:d111::2
2019-05-28 18:06:49,559 - root       - DEBUG    - IPv6 Destination:2001:d111::1
2019-05-28 18:06:49,559 - root       - DEBUG    - Source Type of Service:192
2019-05-28 18:06:49,559 - root       - DEBUG    - Protocol Number:6
2019-05-28 18:06:49,559 - root       - DEBUG    - Protocol:6
2019-05-28 18:06:49,559 - root       - DEBUG    - Source Port:58171
2019-05-28 18:06:49,559 - root       - DEBUG    - Destination Port:179
2019-05-28 18:06:49,559 - root       - DEBUG    - ICMP Type:0
2019-05-28 18:06:49,559 - root       - DEBUG    - ICMP Code:0
2019-05-28 18:06:49,559 - root       - DEBUG    - IPv6 ICMP Type:0
2019-05-28 18:06:49,559 - root       - DEBUG    - Input Interface:552
2019-05-28 18:06:49,560 - root       - DEBUG    - Source VLAN:0
2019-05-28 18:06:49,560 - root       - DEBUG    - IPv6 Source Mask:120
2019-05-28 18:06:49,560 - root       - DEBUG    - IPv6 Destination Mask:128
2019-05-28 18:06:49,560 - root       - DEBUG    - Source AS:2000
2019-05-28 18:06:49,560 - root       - DEBUG    - Destination AS:2000
2019-05-28 18:06:49,560 - root       - DEBUG    - IPv6 Next Hop:2001:d111::1
2019-05-28 18:06:49,560 - root       - DEBUG    - TCP Flags:24
2019-05-28 18:06:49,560 - root       - DEBUG    - Output Interface:0
2019-05-28 18:06:49,560 - root       - DEBUG    - Minimum TTL:1
2019-05-28 18:06:49,560 - root       - DEBUG    - Maximum TTL:1
2019-05-28 18:06:49,560 - root       - DEBUG    - Flow End Reason:2
2019-05-28 18:06:49,560 - root       - DEBUG    - Direction:255
2019-05-28 18:06:49,561 - root       - DEBUG    - Dot-1q VLAN ID:0
2019-05-28 18:06:49,561 - root       - DEBUG    - Dot-1q Customer VLAN ID:0
2019-05-28 18:06:49,561 - root       - DEBUG    - Fragment Header Identification Field:0
2019-05-28 18:06:49,561 - root       - DEBUG    - IPv6 Option Headers:0
2019-05-28 18:06:49,561 - root       - DEBUG    - Bytes In:163
2019-05-28 18:06:49,561 - root       - DEBUG    - Packets In:2
2019-05-28 18:06:49,561 - root       - DEBUG    - Flow Start Milliseconds:2019-05-28 18:06:37.824000
2019-05-28 18:06:49,561 - root       - DEBUG    - Flow End Milliseconds:2019-05-28 18:06:47.296000
2019-05-28 18:06:49,561 - root       - DEBUG    - Traffic:BGP
2019-05-28 18:06:49,561 - root       - DEBUG    - Traffic Category:Routing

#IPv4 traffic
2019-05-28 18:06:57,579 - root       - DEBUG    - Flow Type:IPFIX
2019-05-28 18:06:57,579 - root       - DEBUG    - Sensor:200.0.0.1
2019-05-28 18:06:57,580 - root       - DEBUG    - Sequence:18074
2019-05-28 18:06:57,580 - root       - DEBUG    - Observation Domain:524288
2019-05-28 18:06:57,580 - root       - DEBUG    - Time:2019-05-28T18:06:57.579Z
2019-05-28 18:06:57,580 - root       - DEBUG    - IP Protocol Version:4
2019-05-28 18:06:57,580 - root       - DEBUG    - IPv4 Source:102.0.0.2
2019-05-28 18:06:57,580 - root       - DEBUG    - IPv4 Destination:102.0.0.1
2019-05-28 18:06:57,580 - root       - DEBUG    - Source Type of Service:192
2019-05-28 18:06:57,580 - root       - DEBUG    - Protocol Number:6
2019-05-28 18:06:57,580 - root       - DEBUG    - Protocol:6
2019-05-28 18:06:57,580 - root       - DEBUG    - Source Port:54791
2019-05-28 18:06:57,580 - root       - DEBUG    - Destination Port:179
2019-05-28 18:06:57,581 - root       - DEBUG    - ICMP Type:0
2019-05-28 18:06:57,581 - root       - DEBUG    - ICMP Code:0
2019-05-28 18:06:57,581 - root       - DEBUG    - IPv4 ICMP Type:0
2019-05-28 18:06:57,581 - root       - DEBUG    - Input Interface:553
2019-05-28 18:06:57,581 - root       - DEBUG    - Source VLAN:0
2019-05-28 18:06:57,581 - root       - DEBUG    - Source Mask:30
2019-05-28 18:06:57,581 - root       - DEBUG    - Destination Mask:32
2019-05-28 18:06:57,581 - root       - DEBUG    - Source AS:2000
2019-05-28 18:06:57,581 - root       - DEBUG    - Destination AS:2000
2019-05-28 18:06:57,581 - root       - DEBUG    - IPv4 Next Hop:0.0.0.0
2019-05-28 18:06:57,581 - root       - DEBUG    - TCP Flags:24
2019-05-28 18:06:57,582 - root       - DEBUG    - Output Interface:0
2019-05-28 18:06:57,582 - root       - DEBUG    - Minimum TTL:1
2019-05-28 18:06:57,582 - root       - DEBUG    - Maximum TTL:1
2019-05-28 18:06:57,582 - root       - DEBUG    - Flow End Reason:2
2019-05-28 18:06:57,582 - root       - DEBUG    - BGP IPv4 Next Hop:0.0.0.0
2019-05-28 18:06:57,582 - root       - DEBUG    - Direction:255
2019-05-28 18:06:57,582 - root       - DEBUG    - Dot-1q VLAN ID:0
2019-05-28 18:06:57,582 - root       - DEBUG    - Dot-1q Customer VLAN ID:0
2019-05-28 18:06:57,582 - root       - DEBUG    - Fragment Header Identification Field:0
2019-05-28 18:06:57,582 - root       - DEBUG    - Bytes In:123
2019-05-28 18:06:57,583 - root       - DEBUG    - Packets In:2
2019-05-28 18:06:57,583 - root       - DEBUG    - Flow Start Milliseconds:2019-05-28 18:06:45.248000
2019-05-28 18:06:57,583 - root       - DEBUG    - Flow End Milliseconds:2019-05-28 18:06:47.296000
2019-05-28 18:06:57,583 - root       - DEBUG    - Traffic:BGP
2019-05-28 18:06:57,583 - root       - DEBUG    - Traffic Category:Routing
