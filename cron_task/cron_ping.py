#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import MySQLdb as mdb

NETWORK = [
    {'ip': ‘IP_DEVICE_1’, 'name': ‘NAME_DEVICE_1’, 'type': 'desktop'},
    {'ip': 'IP_DEVICE_2’, 'name': 'NAME_DEVICE_2’, 'type': 'phone'},
    {'ip': 'IP_DEVICE_3’, 'name': 'NAME_DEVICE_3’, 'type': 'tablet'},
    {'ip': 'IP_DEVICE_4’, 'name': 'NAME_DEVICE_4’, 'type': 'raspberry'}
]

con = mdb.connect(‘YOUR_HOST’, ‘YOUR_USERNAME’, ‘YOUR_PASSWORD’, ‘YOUR_DATABASE’)
cur = con.cursor()

with con:
    for hostname in NETWORK:
        response = os.system("ping -c 1 -n -W 2 " + hostname['ip'])
        if response == 0:
            cur.execute("INSERT INTO ping(ip, name, type, status, created) VALUES ('" + hostname['ip'] + "', '" + hostname['name'] + "', '" + hostname['type'] + "', 'up', now() ) ")
        else:
            cur.execute("INSERT INTO ping(ip, name, type, status, created) VALUES ('" + hostname['ip'] + "', '" + hostname['name'] + "', '" + hostname['type'] + "', 'down', now() ) ")
