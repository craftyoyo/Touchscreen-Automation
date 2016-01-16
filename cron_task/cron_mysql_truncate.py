import MySQLdb as mdb
import time

con = mdb.connect('HOST', 'USERNAME', 'PASSWORD', 'DATABASE')
cur = con.cursor()


with con:
    cur.execute("TRUNCATE 'cpu'")
    print ('Truncate cpu, done !')
    time.sleep(1)
    cur.execute("TRUNCATE 'network'")
    print ('Truncate network, done !')
    time.sleep(1)
    cur.execute("TRUNCATE 'sensors'")
    print ('Truncate sensors, done !')
    time.sleep(1)
