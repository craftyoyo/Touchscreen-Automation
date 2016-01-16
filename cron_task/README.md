# Raspberry Home Control

### Crontab : 
in the cron_task you'll find some scripts to check en save some informations (each file need to be modified :
* CPU Temp with cron_cpu_temp.py
* Temp/Humidity with cron_dht22.py
* Ping some IP(s) with cron_ping.py
* Truncate tables with cron_mysql_truncate.py


Personally I use [gnome-schedule](http://gnome-schedule.sourceforge.net/) ```sudo apt-get install gnome-schedule``` (yes, i know, it use Gnome and Raspbian LXCFE shame on me ...)

Start the program ```sudo gnome-schedule```

* cron_cpu_temp.py each 30 minutes
* cron_dht22.py each hour
* cron_ping.py each 5 minutes
* cron_mysql_truncate each month
