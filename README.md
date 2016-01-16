# Raspberry Home Control

![Index](http://i.imgur.com/tN02Tov.png)

This project use : 
* [OpenWeatherMap](http://openweathermap.org/)*
* [Pushbullet](https://www.pushbullet.com/)*
* [MPD](http://www.musicpd.org/)
* Gmail (Calendar)
* [Flask](http://flask.pocoo.org/)

_You'll have to create an account to use the API._
Some apps : 
* gnome-schedule ```sudo apt-get install gnome-schedule```
* xscreensaver ```sudo apt-get install xscreensaver```
* MPD / MPC ```sudo apt-get install mpd mpc```

Some Libs (html/js): 
* [Fullcalendar](http://fullcalendar.io/)
* [Mottie/Keyboard](https://github.com/Mottie/Keyboard)
* [Font-Awesome](https://fortawesome.github.io/Font-Awesome/)
* [Owfont](http://websygen.github.io/owfont/)
* [ChartJs](http://www.chartjs.org/)
* [PickaDate](http://amsul.ca/pickadate.js/) (DatePicker and TimePicker)

And is running on Raspberry Pi 2, Raspbian (Jessie) and [15.6" touchscreen](http://www.chalk-elec.com/?page_id=1280#!/15-6-HDMI-interface-LCD-with-capacitive-touchscreen/p/38127425/category=3094861).

### Update your Pi:

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo rpi-update
```
### MySQL : 
```
sudo apt-get install mysql-server mysql-client python-mysqldb
sudo nano /etc/mysql/my.cnf
```
Search [mysqld] and bind-address replace by the Pi's address
```
bind-address = 192.168.0.2 # For me
```
When you're sure MySQL is working, dump the dump.sql file or just create all tables manually
```
DROP TABLE IF EXISTS `cpu`;

CREATE TABLE `cpu` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `temp` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ping`;

CREATE TABLE `ping` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(100) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `status` varchar(11) DEFAULT '',
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `sensors`;

CREATE TABLE `sensors` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `temperature` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

### Install all the dependances : 
```
sudo apt-get install build-essential python-dev
sudo apt-get install mpd mpc
sudo pip install Flask
sudo pip install flask-bootstrap
sudo pip install flask-appconfig
sudo pip install flask-mysql
sudo pip install python-mpd2
sudo pip install psutil
sudo pip install feedparser
sudo pip install pushbullet.py
sudo pip install --upgrade google-api-python-client
```

### MPD:
Edit the configuration file ```sudo nano /etc/mpd.conf```

```
music_directory		"/media/usbKey/Musiques"
playlist_directory		"/media/usbKey/Playlists"
```
Comment
```
#user				"mpd"
#group                          "nogroup"
#bind_to_address		"localhost"
```
for the audio output I use ALSA if you use something else, just check Google to know ho to modified this part.

```
audio_output {
	type		"alsa"
	name		"My Alsa Device"
	device		"hw:0,0"
}
```
When it's done, reload the configuration file
```sudo /etc/init.d/mpd force-restart```

### DHT22 (Thanks Adafruit) :

```
cd Desktop
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT 
sudo python setup.py install 
cd ../ 
sudo rm -rf Adafruit_Python_DHT
```

### Google (Calendar)
* Create a new project on the [Google Developers Console](https://console.developers.google.com/)
* Enable the Calendars API
* Create new Client ID for standalone application and download the JSON as client_secrets.json and set client_secret_file = 'client_secrets.json' in config.cfg

### Crontab : 
in the cron_task you'll find some scripts to check en save some informations (each file need to be modified :
* CPU Temp with cron_cpu_temp.py
* Temp/Humidity with cron_dht22.py
* Ping some IP(s) with cron_ping.py

Personally I use [gnome-schedule](http://gnome-schedule.sourceforge.net/) ```sudo apt-get install gnome-schedule``` (yes, i know, it use Gnome and Raspbian LXCFE shame on me ...)

Start the program ```sudo gnome-schedule```

* cron_cpu_temp.py each 30 minutes
* cron_dht22.py each hour
* cron_ping.py each 5 minutes

(little advice, don't forget the "python" command before your file ^^)


Finally when everything is done go to the folder and run it with 
```sudo python run.py```

### Configuration file (config.cfg)
This file is not really difficult to edit. Just be careful to put the right datas :

```
SECRET_KEY = 'c9p2Ie41R931iLXS1W4v0cbr0Wm533j2Md37b4w16n3dbX'
DEBUG = 'True'
INTERNET = 'wlan0' # wlan0 or eth0

MYSQL = {
    'host' : 'SQL HOST', # Generally it's "localhost"
    'user' : 'SQL USERNAME',
    'password' : 'SQL PASSWORD',
    'database' : 'SQL DATABASE'
}

I use BCM name for pin number so it's "26" for GPIO 26 and not "37"
PINS = {
    21 : {'name' : 'Hall',          'state' : '', 'type' : 'production'},
    20 : {'name' : 'Living Room',   'state' : '', 'type' : 'production'},
    16 : {'name' : 'D. Room',       'state' : '', 'type' : 'production'},
    26 : {'name' : 'Kitchen',       'state' : '', 'type' : 'production'},
    19 : {'name' : 'Bathroom',      'state' : '', 'type' : 'production'},
    13 : {'name' : 'Bedroom 1',     'state' : '', 'type' : 'production'},
    12 : {'name' : 'Bedroom 2',     'state' : '', 'type' : 'production'}
}

# State's always empty and Type  always "production"

DHT22_PIN = '4' #GPIO 4

GMAIL = {
    'calendar_id' : 'ID OF YOUR CALENDAR@group.calendar.google.com',
    'client_secret_file' : 'raspi-flask.json'
}

FEEDS = {
    'feed_1' : 'http://www.raspberrypi-spy.co.uk/feed/',
    'feed_2' : 'http://www.recantha.co.uk/blog/?feed=rss2',
}

MPD = {
    'host' : 'localhost',
    'port' : '6600'
}

WEATHER = {
    'apikey' : 'YOUR API KEY',
    'city' : 'YOUR CITY',
    'units' : 'metric', # metric  (°C) or imperial  (F)
    'lang' : 'en'
}

PUSHBULLET = {
    'apiKey': 'YOUR API KEY',
    'mail': 'YOUR E-MAiL'
}
```



# Warning 
Pushbullet(Message), MPD (Player) doesn't work really well and it's almost configured only **for me**.

For Pushbullet I create an account ONLY for the pi who send to a contact (me)
That's why you can see **line 391**:

```pb.push_note('[Notification Rpi]', request.form['Content'], contact=pb.contacts[0])```

pv.contacts[0] = my email address

Finally, if you want to correct the code or add something in the documentation (and correct my crappy english..) you're more than welcome ;) 
