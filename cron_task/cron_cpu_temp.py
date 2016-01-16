import os
import MySQLdb as mdb

con = mdb.connect(‘YOUR_HOST’, ‘YOUR_USERNAME’, ‘YOUR_PASSWORD’, ‘YOUR_DATABASE’)
cur = con.cursor()


def tempformat(value):
    return value.replace("temp=", "").replace("'C\n", "")

with con:
    value = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    cur.execute("INSERT INTO cpu(temp, created) VALUES ('" + tempformat(value) + "', now() ) ")
