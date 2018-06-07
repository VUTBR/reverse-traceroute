# Rtraceroute -- Reverse traceroute tool

Tool for reverse path discovery using RIPE probes

# Getting Started

Tool relies on several packages, to install those packages, run:
```
pip install -r requirements.txt
```
Also, paris-traceroute (or at least mtr) package needs to be installed.
Graphs are generated using dot language and graphviz.

```
# sudo dnf install -y paris-traceroute mtr graphviz
```

                    
# Usage:

Make sure that valid API key is present in rtraceroute/config.py file
Running paris traceroute requires root priviledges.

```
python rtraceroute [OPTIONS] destination-host
OPTIONS:
--local-host <local_host>           Host the RIPE traceroute is targeted to, defaults to this machine's address
--protocol [tcp, udp, icmp]         Protocol to use - ICMP, UDP, TCP, defaults to ICMP
--probe-count <count>               Number of RIPE probes to request
--description <description>         Measurement description
--compact                           Compact output, show only AS path and Hostname path
-v, --verbose                       verbose output
```

# Example:
```
sudo python rtaceroute.py --protocol udp -v www.fit.vutbr.cz
```

Average run time is about 1 - 2 minutes. But it depends on Atlas probe responsiveness, occasionally it may take up to 5 minutes.
