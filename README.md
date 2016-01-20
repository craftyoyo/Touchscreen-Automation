# Raspberry Home Control

![Index](http://i.imgur.com/tN02Tov.png)

This project uses the following technologies:
* [OpenWeatherMap](http://openweathermap.org/) \*
* [Pushbullet](https://www.pushbullet.com/) \*
* Gmail (Calendar functionality) \*
* [MPD](http://www.musicpd.org/)
* [Flask](http://flask.pocoo.org/)

_\* You'll have to create an account to use the API._

Dependencies:
* gnome-schedule ```sudo apt-get install gnome-schedule```
* xscreensaver ```sudo apt-get install xscreensaver```
* MPD / MPC ```sudo apt-get install mpd mpc```

HTML/JS libraries used: 
* [Fullcalendar](http://fullcalendar.io/)
* [Mottie/Keyboard](https://github.com/Mottie/Keyboard)
* [Font-Awesome](https://fortawesome.github.io/Font-Awesome/)
* [Owfont](http://websygen.github.io/owfont/)
* [ChartJs](http://www.chartjs.org/)
* [PickaDate](http://amsul.ca/pickadate.js/) (DatePicker and TimePicker)

Running on Raspberry Pi 2, Raspbian (Jessie) with a [15.6" touchscreen](http://www.chalk-elec.com/?page_id=1280#!/15-6-HDMI-interface-LCD-with-capacitive-touchscreen/p/38127425/category=3094861).

## Instructions

### Update your Pi:

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo rpi-update
```

### Install MySQL:
```
sudo apt-get install mysql-server mysql-client python-mysqldb
```

After you have MySQL working, import the **dump.sql** file or just create all the tables manually.

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

### Install all the dependencies:

```
sudo apt-get install build-essential python-dev
sudo apt-get install mpd mpc
sudo pip install Flask
sudo pip install flask-appconfig
sudo pip install flask-mysql
sudo pip install python-mpd2
sudo pip install psutil
sudo pip install feedparser
sudo pip install pushbullet.py
sudo pip install randomavatar
sudo pip install --upgrade google-api-python-client
```

### MPD (music player):
Edit the configuration file:

```
sudo nano /etc/mpd.conf
```

```
music_directory		"/path/to/your/music/folder"
playlist_directory	"/path/to/your/playlist/folder"
```

Comment out these lines:

```
user				"mpd"
group				"nogroup"
bind_to_address		"localhost"
```

I use ALSA for audio output. If you use something else, check Google for instructions on how to modify this part.

```
audio_output {
	type		"alsa"
	name		"My Alsa Device"
	device		"hw:0,0"
}
```

After doing the above changse, reload the configuration file:

```sudo /etc/init.d/mpd force-restart```

### DHT22 temperature-humidity sensor (thanks Adafruit):

```
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python setup.py install
cd ..
sudo rm -rf Adafruit_Python_DHT
```

### Google (Calendar functionality):
* Create a new project on the [Google Developers Console](https://console.developers.google.com/)
* Enable the Calendars API
* Create a new Client ID for standalone application
* Download the JSON as **client_secrets.json**
* Set `client_secret_file = 'client_secrets.json'` in the **config.cfg** file located in the **Touchscreen-Automation** folder

### Crontab:
In the `cron_task` folder you'll find some scripts to check and save data (each file needs to be modified):
* CPU Temperature: **cron_cpu_temp.py**
* Temperature / Humidity: **cron_dht22.py**
* Ping IP address(es): **cron_ping.py**

Personally I use [gnome-schedule](http://gnome-schedule.sourceforge.net/).

```
sudo apt-get install gnome-schedule
```

(yes, I know, it uses GNOME and Raspbian LXCFE, shame on me...)

Start the scheduler:

```
sudo gnome-schedule
```

* Run cron_cpu_temp.py every 30 minutes
* Run cron_dht22.py every hour
* Run cron_ping.py every 5 minutes

*Tip: don't forget the `python` command before your file.*

Finally when everything is done go to the **Touchscreen-Automation** folder and run the application:

```
sudo python run.py
```

### Configuration file (config.cfg):
This file is easy to edit. Just be careful to insert the right values:

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

# I use BCM name for pin number so it's "26" for GPIO 26 and not "37"
# State is always empty and type is always "production"
PINS = {
    21 : {'name' : 'Hall',          'state' : '', 'type' : 'production'},
    20 : {'name' : 'Living Room',   'state' : '', 'type' : 'production'},
    16 : {'name' : 'D. Room',       'state' : '', 'type' : 'production'},
    26 : {'name' : 'Kitchen',       'state' : '', 'type' : 'production'},
    19 : {'name' : 'Bathroom',      'state' : '', 'type' : 'production'},
    13 : {'name' : 'Bedroom 1',     'state' : '', 'type' : 'production'},
    12 : {'name' : 'Bedroom 2',     'state' : '', 'type' : 'production'}
}

DHT22_PIN = '4' # GPIO 4

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
    'units' : 'metric', # metric (°C) or imperial (F)
    'lang' : 'en'
}

PUSHBULLET = {
    'apiKey': 'YOUR API KEY',
    'mail': 'YOUR E-MAiL'
}
```

# Warning:
MPD (music player) doesn't work well and it's configured only **for me**.

Finally, if you want to correct the code or add something in the documentation (and correct my crappy english...) you're more than welcome. ;)
