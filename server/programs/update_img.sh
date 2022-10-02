#!/bin/sh

python3 programs/parse_weather.py
inkscape --export-type="pnp" wallpaper.svg

#We move the image where it needs to be
#rm /var/www/kindle/done.png
#mv done.png /var/www/kindle/done.png
#
#rm basic.ics
#rm after-weather.svg
#rm almost_done.png
#rm almost_done.svg

