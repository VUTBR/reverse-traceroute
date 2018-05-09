Rtraceroute -- Reverse traceroute tool

Installation

Tool relies on several packages, to install those packages, run:
# pip install -r requirements.txt

Usage:
Make sure that valid API key is present in rtraceroute/config.py file

python rtraceroute [OPTIONS] destination-host
OPTIONS:
--local-host <local_host>           Host the RIPE traceroute is targeted to, defaults to this machine's address
--protocol [tcp, udp, icmp]         Protocol to use - ICMP, UDP, TCP, defaults to ICMP
--distant-hosts-file <path/to/file> Run rtraceroute for all hosts in
--probe-count <count>               Number of RIPE probes to request
--description <description>         Measurement description
-v, --verbose                       verbose output
