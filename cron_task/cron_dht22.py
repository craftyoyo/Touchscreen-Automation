import Adafruit_DHT as dht
import MySQLdb as mdb

con = mdb.connect(‘YOUR_HOST’, ‘YOUR_USERNAME’, ‘YOUR_PASSWORD’, ‘YOUR_DATABASE’)
cur = con.cursor()

with con:
    humidity, temperature = dht.read_retry(dht.DHT22, 4)
    cur.execute("INSERT INTO sensors(temperature, humidity, created) VALUES ('" + format(temperature) + "', '" + format(humidity) + "', now() ) ")
