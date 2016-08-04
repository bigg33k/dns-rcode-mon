#!/usr/bin/python
from datetime import datetime
import time
import subprocess
import shlex
import socket
import os
import re
import threading
import dns.resolver
import dns.query
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *
from dns.message import *

DEBUG = False
STATS = False
if STATS:
	import statsd

METRICS = True

#os.nice(20)

CARBON_SERVER = 'localhost'
CARBON_PORT = 2003
STATSD_SERVER=CARBON_SERVER


mydnsrecord="your.domain"
myrecordtype="a"
myauthservername="your.auth.ns"
myauthserverip=socket.gethostbyname(myauthservername)
myhostname=socket.gethostname()
mymetricprefix="edgemon." + re.sub('\.','_',myhostname)
metricauthservername = re.sub('\.', '_', myauthservername)
metricdnsrecord = re.sub('\.','_',mydnsrecord)

HEADER="HEADER"

rrsets=0;
rcode=0;
result="";
answer="";
ns="";
message="";

#send metrics to graphite
def send_metrics():
	global DEBUG
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((CARBON_SERVER,CARBON_PORT))
		sock.send(message)
		sock.close()
		if DEBUG:
			print "\nMetrics sent: " + message
	except:
		print "\nCouldn't send metrics"



if STATS:
	stats= statsd.Connection.set_defaults(host=STATSD_SERVER)

while (1):
	if STATS:
		proptimer = statsd.Timer('edgemon')
		proptimer.start()

	n = mydnsrecord.split(".")
	for i in xrange(len(n), 0, -1):
		sub = '.'.join(n[i-1:])

	#time dns query
	t_start = time.time()
	query = dns.message.make_query(sub, dns.rdatatype.A, dns.rdataclass.IN)
	response = dns.query.udp(query, myauthserverip)
	t_end = time.time()
	t_total = t_end - t_start

	if DEBUG:
		print response

	rcode = response.rcode()
	rrsets = [response.answer]

	# Handle all RRsets, not just the first one
	for rrset in rrsets:
		for rr in rrset:
			if rr.rdtype == dns.rdatatype.SOA:
				if DEBUG:
					print "SOA"
			elif rr.rdtype == dns.rdatatype.A:
				if DEBUG:
					print "A"
					for recs in rr.items:
						answer = re.sub('\.','_',rr.items[0].address)
			elif rr.rdtype == dns.rdatatype.NS:
				if DEBUG:
					print "NS"
				authority = rr.target
				ns = default.query(authority).rrset[0].to_text()
				result = rrset
			elif rr.rdtype == dns.rdatatype.CNAME:
				if DEBUG:
					print "CNAME"
				for rid in rr:
					answer = rid
			else:
				# IPv6 glue records etc
				#log('Ignoring %s' % (rr))
				pass
	#sleepytime
	time.sleep(2)

	if STATS:
		proptimer.stop(mystatsd)

	message = '%s.%s.%s.%s %2f %d\n' % (mymetricprefix,metricdnsrecord,metricauthservername,dns.rcode.to_text(rcode),t_total,time.time())

	if METRICS:
		metrics_thread = threading.Thread(target=send_metrics)
		metrics_thread.start()
