#!/usr/bin/env python
# Nikolai Kristiansen <nikolaik@gmail.com>
import json
import sys
import subprocess
from collections import OrderedDict
import datetime
import requests

import settings

def to_python(status):
    integer_fields = [
        "driver.parameter.pollinterval",
        "ups.delay.shutdown",
        "ups.delay.start",
        "ups.load"
    ]
    float_fields = [
        "battery.voltage",
        "battery.voltage.high",
        "battery.voltage.low",
        "input.frequency",
        "input.voltage",
        "input.voltage.fault",
        "output.voltage",
        "ups.temperature"
    ]
    for k,v in status.items():
        if k in integer_fields:
            v = int(v)
        elif k in float_fields:
            v = float(v)

        status[k] = v

    return status

def get_status(psu_label):
    cmd = ['upsc', psu_label]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = p.communicate()
    
    lines = stdout.strip().split('\n')
    kvs = [l.split(': ') for l in lines]
    status = to_python(OrderedDict(kvs))

    return status

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("Invalid num args.")
        print("Usage: argv[0] psu_label")
        exit(1)
    
    output = {
        'poll_date': datetime.datetime.utcnow().isoformat(),
        'status': get_status(sys.argv[1])
    }
    json_output = json.dumps(output, indent=4)
    try:
        r = requests.post(
            settings.LOGSTASH_URL,
            data=json_output, headers={'content-type':'application/json'},
            auth=(settings.LOGSTASH_USER, settings.LOGSTASH_PASSWORD),
            timeout=10
        )
    except requests.exceptions.Timeout as e:
        print('Could not post data to logstash: {0}'.format(str(e)))
        exit(2)

