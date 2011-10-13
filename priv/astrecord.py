#!/usr/bin/env python

""" Helper function for adding new event records to eastrisk.

Whenever you see an "Unknown Event" message in your log, paste the event into the STDIN of this python
script. It will generate the record definition and the necessary code
to parse the event from the binary stream.

Example format of an event could be pasted:

    name: 'RTPReceiverStat'
    elements: [{'RRCount',"0"},
               {'Transit',"-0.0004"},
               {'Jitter',"0.0069"},
               {'LostPackets',"0"},
               {'ReceivedPackets',"161"},
               {'SSRC',"412556370"},
               {'Privilege',"reporting,all"}]
"""

import sys
import re

event = {'name': 'RTCPSent',
         'elements': [('DLSR',"0.0390 (sec)"),
              ('TheirLastSR',"565029758"),
              ('IAJitter',"0.0069"),
              ('CumulativeLoss',"0"),
              ('FractionLost',"0"),
              ('ReportBlock',[]),
              ('SentOctets',"82434"),
              ('SentPackets',"2498"),
              ('SentRTP',"399680"),
              ('SentNTP',"1318495021.2904420352"),
              ('OurSSRC',"360594771"),
              ('To',"127.0.0.1:7079"),
              ('Privilege',"reporting,all")]}


def lowercase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def sep():
    print 
    print "-------------------"
    print

def convert(event):
    lname = lowercase(event['name'])
    elements = [e for e,m in event['elements']]

    sep()
    print "-record(%s," % lname
    print "{"
    for n,m in event['elements']:
        sys.stdout.write("\t%s" % lowercase(n))
        if n != event['elements'][-1][0]:
            sys.stdout.write(",")
        print
    print "})."

    sep()
    print "parse_event('%s', Elements) ->\n    %s_record(Elements, #%s{}, nil);" % (event['name'], lname, lname)
    sep()

    for e, v in event['elements']:
        val = map_field(e, v)
        if v is not None: continue
        print '%s_record([<<"%s: ", Data/binary>>|T], Record, ActionID) ->' % (lname, e)
        print "    %s_record(T, Record#%s{%s = %s}, ActionID);" % (lname, lname, lowercase(e), val)

    print "%s_record([Field|T], Record, ActionID) ->" % lname
    print '    ?warning(io_lib:format("Ignoring ~p in %s record.", [Field])),' % lname
    print '    %s_record(T, Record, ActionID);' % lname
    print '%s_record([], Record, ActionID) ->' % lname
    print '    {Record, ActionID}.'
    print


def map_field(e, v):
    if e == 'Privilege':
        return 'privileges_list(Data)'
    if re.match("^\d+$", v):
        return "binary_to_integer(Data)"
    if re.match("^\d+\.\d+$", v):
        return "binary_to_float(Data)"
    return 'binary_to_list(Data)'


inp = sys.stdin.read()
inp = inp.replace("{", "(").replace("}", ")").replace("name:", "{'name':").replace("elements:", ",'elements':").replace("[]", '""')+"}"

convert(eval(inp))


