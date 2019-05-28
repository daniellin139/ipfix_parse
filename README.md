# ipfix_parser
# python3 ipfix_parser   //command to start parser
# you can find data output from /var/log/ipfix.log
# Support ipfix(version10) only, tested with the following config on Juniper MX router for both IPv4 and IPv6.
set chassis fpc 0 sampling-instance instance-1

set chassis fpc 0 inline-services flow-table-size ipv4-flow-table-size 8

set chassis fpc 0 inline-services flow-table-size ipv6-flow-table-size 8

set services flow-monitoring version-ipfix template template-v4 flow-active-timeout 10

set services flow-monitoring version-ipfix template template-v4 flow-inactive-timeout 10

set services flow-monitoring version-ipfix template template-v4 template-refresh-rate seconds 10

set services flow-monitoring version-ipfix template template-v4 ipv4-template

set services flow-monitoring version-ipfix template template-v6 flow-active-timeout 10

set services flow-monitoring version-ipfix template template-v6 flow-inactive-timeout 10

set services flow-monitoring version-ipfix template template-v6 template-refresh-rate seconds 30

set services flow-monitoring version-ipfix template template-v6 ipv6-template

set forwarding-options sampling instance instance-1 input rate 1

set forwarding-options sampling instance instance-1 family inet output flow-server 200.0.0.2 port 2055

set forwarding-options sampling instance instance-1 family inet output flow-server 200.0.0.2 version-ipfix template template-v4

set forwarding-options sampling instance instance-1 family inet output inline-jflow source-address 200.0.0.1

set forwarding-options sampling instance instance-1 family inet output inline-jflow flow-export-rate 10

set forwarding-options sampling instance instance-1 family inet6 output flow-server 200.0.0.2 port 2055

set forwarding-options sampling instance instance-1 family inet6 output flow-server 200.0.0.2 version-ipfix template template-v6

set forwarding-options sampling instance instance-1 family inet6 output inline-jflow source-address 200.0.0.1

set forwarding-options sampling instance instance-1 family inet6 output inline-jflow flow-export-rate 10

set firewall family inet filter ipv4-sample term 1 then sample

set firewall family inet filter ipv4-sample term 1 then accept

set firewall family inet6 filter ipv6-smaple term 1 then sample

set firewall family inet6 filter ipv6-smaple term 1 then accept
