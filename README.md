# FitBot

Python script to automate your booking sessions in [aimharder.com](http://aimharder.com) platform

1) fill settings.py
2) `make virtualenv`
3) `venv/bin/python main.py`


## Install
```sh
make virtualenv
```

## Run
```sh
venv/bin/python main.py
Session booked for your_email@domain.com on 20190909 at 1730_60
```

## Schedule the script
You can use crontab to schedule this script for example everyday at 00:01

```sh
1 0 * * * /home/pi/Desktop/fitbot/venv/bin/python /home/pi/Desktop/fitbot/main.py
```
Enjoy!
