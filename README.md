Adaption of https://github.com/bigg33k/dnsmon to measure a specific node entry for response, RCODE, and other stuff.
The results are pushed to graphite using statsd. python-statsd is required for these to work.

I used this crontab to manage things:

`m h  dom mon dow   command
@reboot /usr/bin/python /home/dns-rcode-mon/dnsedge-ms-ns1.py >>/home/dns-rcode-mon/logs/dnsedge-ns1.log
@reboot /usr/bin/python /home/dns-rcode-mon/dnsedge-ms-ns2.py >>/home/dns-rcode-mon/logs/dnsedge-ns2.log
@reboot /usr/bin/python /home/dns-rcode-mon/dnsedge-ms-ns3.py >>/home/dns-rcode-mon/logs/dnsedge-ns3.log
@reboot /usr/bin/python /home/dns-rcode-mon/dnsedge-ms-ns4.py >>/home/dns-rcode-mon/logs/dnsedge-ns4.log`
