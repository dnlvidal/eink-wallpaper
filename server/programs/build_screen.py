import urllib.request, json 
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import codecs
import os
import time

from icalendar import Calendar

with open('config.json', 'r') as f:
    cfg = json.load(f)

# Start writing SVG
WIDTH=600
HEIGHT=800
f = codecs.open('wallpaper.svg', 'w', encoding='utf-8')
f.write("""
<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <style>
    .w_tstamp   { font: 14px sans-serif; }
    .w_temp     { font: 18px sans-serif; }
    .w_cal_item { font: 18px sans-serif; }
    .w_cal_date { font: 18px sans-serif; }
  </style>
<rect x="0" width="600" height="800" fill="none" stroke="black"
  />
"""%(WIDTH,HEIGHT))

#########################################
# Parse weather and write forecast array
#########################################

n2w = {
  "0":"Dom",
  "1":"Seg",
  "2":"Ter",
  "3":"Qua",
  "4":"Qui",
  "5":"Sex",
  "6":"Sab"
}

def tstamp2str(tstamp):
  tstamp2format = datetime.utcfromtimestamp(tstamp)
  weekday = n2w[tstamp2format.strftime("%w")]
  tstamp_str = tstamp2format.strftime(" %-Hh")
  return weekday+tstamp_str

# Read the JSON
with urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?" + cfg["OWM_CODE"] + "&appid=" + cfg["OWM_KEY"] + "&units=metric") as url:
    data = json.loads(url.read().decode())

#print(json.dumps(data, indent=4))

with urllib.request.urlopen("http://api.openweathermap.org/data/2.5/forecast?" + cfg["OWM_CODE"] + "&appid=" + cfg["OWM_KEY"] + "&units=metric&cnt=32") as url:
    forecast = json.loads(url.read().decode())

#print(json.dumps(forecast, indent=4))


## Get API info
#low   = data["main"]["temp_min"]
#high  = data["main"]["temp_max"]
#image = data["weather"][0]["id"]
#
## This tells if it is night "n" or day "d"
#light = data["weather"][0]["icon"][-1:]
#
## Extra info
#date = date.today().strftime("%d %b %Y")
#
## Get the correct icon

icon_size = 40;
half_margin = 20;
temp_space = 0;
day_space = 15;
icons_path = "../icons/"
y_inner_space=5
temp_height=18
date_height=16

cal_item_height=18
cal_date_width=cal_item_height

rel_date_y = date_height
rel_temp_y = y_inner_space+rel_date_y+temp_height
rel_icon_y = y_inner_space+rel_temp_y
rel_hline_y= y_inner_space+rel_icon_y+icon_size
arr_y = 0;
arr_x = 0; 
x_step = WIDTH/8;
rel_icon_x = (x_step-icon_size)/2
rel_text_x = x_step/2
hcount=0
for f_item in forecast["list"]:
  tstamp = tstamp2str(f_item["dt"])
  temp   = f_item["main"]["temp"]
  image = f_item["weather"][0]["id"]
  light = f_item["weather"][0]["icon"][-1:]
  image_path = icons_path + str(image) + light + '.svg'
  if not os.path.exists(image_path):
    print(json.dumps(f_item, indent=4))
    print(image_path)
    image_path = icons_path+'error.svg'
  svg_icon='<image x="%d" y="%d" xlink:href="%s" height="%d" width="%d" />'            %(arr_x+rel_icon_x,arr_y+rel_icon_y,image_path,icon_size,icon_size)
  svg_temp='<text  x="%d" y="%d" text-anchor="middle" class="w_temp">%d°C</text>'%(arr_x+rel_text_x,arr_y+rel_temp_y,temp)
  svg_day ='<text  x="%d" y="%d" text-anchor="middle" class="w_tstamp">%s</text>'%(arr_x+rel_text_x,arr_y+rel_date_y,tstamp)
  f.write(svg_day+"\n")
  f.write(svg_temp+"\n")
  f.write(svg_icon+"\n")
  arr_x += x_step;
  if arr_x >= WIDTH :
    f.write('<line x1="%d" x2="%d" y2="%d" y1="%d" stroke="gray" />'%(y_inner_space,WIDTH-y_inner_space, arr_y+rel_hline_y,arr_y+rel_hline_y))
    arr_x = 0;
    arr_y += rel_hline_y

arr_y += 1
f.write('<line x1="%d" x2="%d" y2="%d" y1="%d" stroke="black" />'%(y_inner_space,WIDTH-y_inner_space, arr_y,arr_y))

#############################################
# Parse Calendars

def get_start( event ):
    return event['DTSTART'].dt.strftime("%y%m%d%h%m")

events = []

for cal_url in cfg["CAL"]:
    urllib.request.urlretrieve(cal_url, "basic.ics")
    cal = Calendar.from_ical(open('basic.ics','rb').read())
    for component in cal.walk('vevent'):
        events.append(component)



events.sort(key=get_start)

cal_y= arr_y+cal_item_height
cal_x=y_inner_space
count=0
for event in events:
    date_start = event['DTSTART'].dt
    date_end   = event['DTEND'].dt
    entry_day  = date_start.strftime("%d")
    entry_month = date_start.strftime("%m")
    entry_name = event['SUMMARY'] 
    event_yday = date_start.timetuple().tm_yday
    event_year = date_start.timetuple().tm_year
    now_yday = datetime.now().timetuple().tm_yday
    now_year = datetime.now().timetuple().tm_year
    if ( event_year >= now_year) and (event_yday >= now_yday):
      f.write('<text  x="%d" y="%d" class="w_cal_date">%s</text>'%(cal_x,cal_y,entry_day))
      cal_x += cal_date_width + y_inner_space
      f.write('<text  x="%d" y="%d" class="w_cal_date">%s</text>'%(cal_x,cal_y,entry_month))
      cal_x += cal_date_width + 2*y_inner_space
      f.write('<text  x="%d" y="%d" class="w_cal_item">%s</text>'%(cal_x,cal_y,entry_name))
      cal_y += y_inner_space + y_inner_space
      f.write('<line x1="%d" x2="%d" y2="%d" y1="%d" stroke="gray" />'%(y_inner_space,WIDTH-y_inner_space,cal_y ,cal_y))
      count+=1
      if count > 5:
          break
      else:
          cal_x = y_inner_space
          cal_y += cal_item_height+y_inner_space

# Close SVG
f.write('</svg>')

#from cairosvg import svg2png
#svg2png(url='wallpaper.svg',write_to='wallpaper.png')

