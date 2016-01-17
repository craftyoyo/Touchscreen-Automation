#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, redirect, request, url_for
from flask_appconfig import AppConfig
from flaskext.mysql import MySQL
from datetime import datetime

from apiclient import discovery
from oauth2client import client, tools
import oauth2client
import httplib2

import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import feedparser
from pushbullet import Pushbullet
from mpd import MPDClient

import time
import os
import psutil
import socket
import fcntl
import struct
import json
import urllib2


def create_app(configfile='config.cfg'):
    app = Flask(__name__)
    AppConfig(app, configfile)
    app.debug = app.config['DEBUG']
    mysql = MySQL()
    pb = Pushbullet(app.config['PUSHBULLET']['apiKey'])
    app.config['MYSQL_DATABASE_HOST'] = app.config['MYSQL']['host']
    app.config['MYSQL_DATABASE_USER'] = app.config['MYSQL']['user']
    app.config['MYSQL_DATABASE_PASSWORD'] = app.config['MYSQL']['password']
    app.config['MYSQL_DATABASE_DB'] = app.config['MYSQL']['database']
    mysql.init_app(app)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    pins = app.config['PINS']
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    def get_credentials():
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'flask-calendar.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(app.config['GMAIL']['client_secret_file'], 'https://www.googleapis.com/auth/calendar')
            flow.user_agent = 'Raspberry Flask Calendar'
            flags = tools.argparser.parse_args(args=[])
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)
        return credentials

    def bytes2human(n):
        symbols = (' Ko', ' Mo', ' Go', ' To', ' Po', ' Eo', ' Zo', ' Yo')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n

    def getRevision():
      revision = "ERROR"
      try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
          if line[0:8] == 'Revision':
            revision = line[11:15]
            full_revision = line[11:17]
        f.close()
      except:
        revision = "ERROR"
      if revision[0] == "a" or revision[0] == "9":
        revision = full_revision
      return revision

    def revToModel():
      rev = getRevision()
      model = [
        "0002", ["Model B Rev 1.0", "256MB"],
        "0003", ["Model B Rev 1.0 (no fuses,D14)", "256MB"],
        "0004", ["Model B Rev 2.0 (mounting holes,Sony)", "256MB"],
        "0005", ["Model B Rev 2.0 (mounting holes,Qisda)", "256MB"],
        "0006", ["Model B Rev 2.0 (mounting holes,Egoman)", "256MB"],
        "0007", ["Model A (Egoman)", "256MB"],
        "0008", ["Model A (Sony)", "256MB"],
        "0009", ["Model A (Qisda)", "256MB"],
        "000d", ["Model B Rev 2.0 (mounting holes,Egoman)", "512MB"],
        "000e", ["Model B Rev 2.0 (mounting holes,Sony)", "512MB"],
        "000f", ["Model B Rev 2.0 (mounting holes,Qisda)", "512MB"],
        "0010", ["Model B+", "512MB"],
        "0011", ["Compute Module", "512MB"],
        "0012", ["Model A+", "256MB"],
        "0014", ["Compute Module", "512MB"],
        "900092", ["PiZero", "512MB"],
        "a01041", ["Model 2B (Sony)", "1GB"],
        "a21041", ["Model 2B (Embest)", "1GB"]
      ]
      ix = model.index(rev)
      board, memory = model[ix+1]
      return (rev, board, memory)

    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', ifname[:15])
        )[20:24])

    def datetimeformat(value, format='%H:%M'):
        return value.strftime(format)

    def timestampformat(value, format='%Y-%m-%d %H:%M:%S'):
        return datetime.fromtimestamp(int(value)).strftime(format)

    def tempformat(value):
        return value.replace("temp=", "").replace("'C\n", "")

    def dhtformat(value):
        return int(value)

    def duration(value):
        return datetime.fromtimestamp(int(value)).strftime('%M:%S')

    def currentDuration(value):
        tmp = value.split(':')
        duration = datetime.fromtimestamp(int(tmp[0])).strftime('%M:%S')
        return duration

    def timeAgo(time=False):
        now = datetime.now()
        if type(time) is int:
            diff = now - datetime.fromtimestamp(time)
        elif isinstance(time, datetime):
            diff = now - time
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff / 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff / 7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff / 30) + " months ago"
        return str(day_diff / 365) + " years ago"

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['timestampformat'] = timestampformat
    app.jinja_env.filters['tempformat'] = tempformat
    app.jinja_env.filters['dhtformat'] = dhtformat
    app.jinja_env.filters['duration'] = duration
    app.jinja_env.filters['timeAgo'] = timeAgo
    app.jinja_env.filters['currentDuration'] = currentDuration

    @app.route('/')
    def index():
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * FROM (SELECT * FROM sensors ORDER BY id DESC limit 8) AS sensors ORDER BY id ASC")
        sensors = cursor.fetchall()

        for pin in pins:
            pins[pin]['state'] = GPIO.input(pin)

        jsonWeather = urllib2.urlopen('http://api.openweathermap.org/data/2.5/forecast/daily?q=' + app.config['WEATHER']['city'] + '&units=' + app.config['WEATHER']['units'] + '&lang=' + app.config['WEATHER']['lang'] + '&appid=' + app.config['WEATHER']['apikey'] + '&cnt=6&mode=json')
        weather = json.load(jsonWeather)

        templateData = {
            'sensors': sensors,
            'pins': pins,
            'weather': weather
        }
        return render_template('index.html', **templateData)

    @app.route('/sensor')
    def sensor():
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * FROM (SELECT * FROM sensors ORDER BY id DESC limit 24) AS sensors ORDER BY id ASC")
        sensors = cursor.fetchall()
        templateData = {
            'sensors': sensors,
            'realtime': dht.read_retry(dht.DHT22, app.config['DHT22_PIN'])
        }
        return render_template('sensor.html', **templateData)

    @app.route('/switch')
    def switch():

        for pin in pins:
            pins[pin]['state'] = GPIO.input(pin)

        templateData = {
            'pins': pins
        }
        return render_template('switch.html', **templateData)

    @app.route('/switch/<master>')
    def master(master):
        if master == 'on':
            for pin in pins:
                GPIO.output(pin, GPIO.HIGH)

        if master == 'off':
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)

        if master == 'toggle':
            for pin in pins:
                GPIO.output(pin, not GPIO.input(pin))

        if master == 'reset':
            for pin in pins:
                GPIO.output(pin, GPIO.LOW)
                time.sleep(5)
                GPIO.output(pin, GPIO.HIGH)

        return redirect(url_for('switch'))

    @app.route('/switch/<changePin>/<action>')
    def action(changePin, action):
        changePin = int(changePin)

        if action == 'on':
            GPIO.output(changePin, GPIO.HIGH)

        if action == 'off':
            GPIO.output(changePin, GPIO.LOW)

        if action == 'toggle':
            GPIO.output(changePin, not GPIO.input(changePin))

        if action == 'reset':
            GPIO.output(changePin, GPIO.LOW)
            time.sleep(5)
            GPIO.output(changePin, GPIO.HIGH)

        return redirect(url_for('switch'))

    @app.route('/calendar')
    def calendar():
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        events = service.events().list(singleEvents=True, calendarId=app.config['GMAIL']['calendar_id']).execute()
        today = datetime.today()
        now = today.strftime('%Y-%m-%d')

        templateData = {
            'now': now,
            'agenda': events['items']
        }

        return render_template('calendar.html', **templateData)

    @app.route('/calendar/add', methods=['POST'])
    def add():
        if request.method == 'POST':
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)

            start = ""+request.form['StartDate']+"T"+request.form['StartTime']+":00+01:00"
            end = ""+request.form['EndDate']+"T"+request.form['EndTime']+":00+01:00"

            event = {
                "summary": request.form['Summary'],
                "description": request.form['Description'],
                "start": {
                    "dateTime": start,
                    "timeZone": "Europe/Paris"
                },
                "end": {
                    "dateTime": end,
                    "timeZone": "Europe/Paris"
                }
            }
            service.events().insert(calendarId=app.config['GMAIL']['calendar_id'], body=event).execute()
        return redirect(url_for('calendar'))

    @app.route('/calendar/delete/<idevent>')
    def delete(idevent):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        service.events().delete(calendarId=app.config['GMAIL']['calendar_id'], eventId=idevent).execute()

        return redirect(url_for('calendar'))

    @app.route('/feed')
    def feed():

        templateData = {
            'rspy': feedparser.parse(app.config['FEEDS']['feed_1']),
            'rpypod': feedparser.parse(app.config['FEEDS']['feed_2'])
        }

        return render_template('feed.html', **templateData)

    @app.route('/player')
    def player():
        client = MPDClient()
        client.connect(app.config['MPD']['host'], app.config['MPD']['port'])
        client.timeout = None
        client.idletimeout = None

        splitTemp = client.status()['time']
        split = splitTemp.split(':')

        templateData = {
            'variable': (int(split[0]) * 100) / int(split[1]),
            'status': client.status(),
            'current': client.currentsong(),
            'playlist': client.playlistinfo()
        }

        return render_template('player.html', **templateData)

    @app.route('/player/<player_action>')
    def player_action(player_action):
        client = MPDClient()
        client.connect(app.config['MPD']['host'], app.config['MPD']['port'])
        client.timeout = None
        client.idletimeout = None

        if player_action == 'backward':
            client.previous()
        elif player_action == 'forward':
            client.next()
        elif player_action == 'play':
            client.play()
        elif player_action == 'pause':
            client.pause()

        return redirect(url_for('player'))

    @app.route('/player/play/<play_id>')
    def play_id(play_id):
        client = MPDClient()
        client.connect(app.config['MPD']['host'], app.config['MPD']['port'])
        client.timeout = None
        client.idletimeout = None
        client.playid(play_id)
        return redirect(url_for('player'))

    @app.route('/message')
    def message():
        templateData = {
            'my_adress': app.config['PUSHBULLET']['mail'],
            'contacts': pb.contacts,
            'logs': pb.get_pushes()
        }
        return render_template('message.html', **templateData)

    @app.route('/message/send', methods=['POST'])
    def send_push():
        if request.method == 'POST':
            pb.push_note('[Notification Rpi]', request.form['Content'], email=request.form['Contact'])

        return redirect(url_for('message'))

    @app.route('/message/delete/<iden>')
    def delete_push(iden):
        pb.delete_push(iden)
        return redirect(url_for('message'))

    @app.route('/camera')
    def camera():

        return render_template('camera.html')

    @app.route('/system')
    def system():
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * FROM (SELECT * FROM cpu ORDER BY id DESC limit 24) AS cpu ORDER BY id ASC")
        cpu_graph = cursor.fetchall()

        templateData = {
            'cpu_graph': cpu_graph,
            'uname': os.uname(),
            'ip': get_ip_address(app.config['INTERNET']),
            'raspberry': revToModel(),
            'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0],
            'cpu': str(psutil.cpu_percent()),
            'cpu_temp': os.popen('/opt/vc/bin/vcgencmd measure_temp').readline(),
            'mem_percent': memory.percent,
            'mem_used': bytes2human(memory.used),
            'mem_total': bytes2human(memory.total),
            'disk_used': bytes2human(disk.used),
            'disk_total': bytes2human(disk.total),
            'disk_percent': disk.percent
        }
        return render_template('system.html', **templateData)

    @app.route('/network')
    def network():
        ping_cur = mysql.connect().cursor()
        ping_cur.execute("SELECT * FROM (SELECT * FROM ping ORDER BY id DESC limit 5) AS ping ORDER BY id ASC")
        ping = ping_cur.fetchall()

        templateData = {
            'ping': ping
        }
        return render_template('network.html', **templateData)

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=80)
