from requests_oauthlib import OAuth1
from urllib.parse import quote
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import requests, urllib.request, logging
from PIL import Image, ImageFont, ImageDraw, ImageTk
from twython import Twython

logging.basicConfig(level = logging.INFO)
twitter = Twython('',
                  '',
                  '',
                  '')

coc_token = ''
tag = quote('#2VY9RYQC')
main_api = 'https://api.clashofclans.com/v1/clans/%s/warlog'%tag
date_format = '%Y%m%dT%H%M%S.%fZ'
date_format2 = '%Y-%m-%d %H:%M:%S.%f'
delta = timedelta(minutes = 5)

def get_tweet(data):  
    
    if (data['result'] == 'win'):
        result = 'Victory!'
        background = Image.open('victory.png')
        fill = (0, 200, 46, 255)
    elif (data['result'] == 'lose'):
        result = 'Defeat'
        background = Image.open('defeat.png')
        fill = (190, 0, 0, 255)
    else:
        result = 'Draw'
        background = Image.open('defeat.png')
        fill = (176, 165, 144, 255)
    
    war_size = '%s vs %s'%(data['teamSize'], data['teamSize'])
    stars_us = str(data['clan']['stars'])
    stars_them = str(data['opponent']['stars'])
    dest_us = '{0:.1f}'.format(data['clan']['destructionPercentage']) + '%'
    dest_them = '{0:.1f}'.format(data['opponent']['destructionPercentage']) + '%'
    urllib.request.urlretrieve(data['clan']['badgeUrls']['large'], 'us.png')
    urllib.request.urlretrieve(data['opponent']['badgeUrls']['large'], 'opponent.png')

    shield_us = Image.open('us.png')
    shield_us = shield_us.resize((350, 350), Image.ANTIALIAS)
    shield_opponent = Image.open('opponent.png')
    shield_opponent = shield_opponent.resize((350, 350), Image.ANTIALIAS)

    wid = 1920
    box_us = (int(wid/3-350/2)-100, 100, int(wid/3+350/2)-100, 450)
    box_opponent = (int(2*wid/3-350/2)+100, 100, int(2*wid/3+350/2)+100, 450)

    background.paste(shield_us, box_us, shield_us)
    background.paste(shield_opponent, box_opponent, shield_opponent)

    font = ImageFont.truetype('font.ttf', 100)
    draw = ImageDraw.Draw(background)
    w, h = draw.textsize(result, font = font)
    draw.text(((wid-w)/2, 500), result, font = font, fill = fill)
    
    w, h = draw.textsize('VS', font = font)
    draw.text(((wid-w)/2, 380), 'VS', font = font, fill = (190,0,0, 255))
    font = ImageFont.truetype('font.ttf', 60)

    w, h = draw.textsize(war_size, font = font)
    draw.text(((wid-w)/2, 600), war_size, font = font)

    w, h = draw.textsize(data['clan']['name'], font = font)
    draw.text((int(wid/3-w/2)-100, 400), data['clan']['name'], font = font)

    w, h = draw.textsize(data['opponent']['name'], font = font)
    draw.text((int(2*wid/3-w/2)+100, 400), data['opponent']['name'], font = font)

    w, h = draw.textsize(stars_us + '*', font = font)
    draw.text((int(wid/3-w/2)-100, 700), stars_us + '*', font = font)

    w, h = draw.textsize(stars_them + '*', font = font)
    draw.text((int(2*wid/3-w/2)+100, 700), stars_them + '*', font = font)
    
    w, h = draw.textsize(dest_us, font = font)
    draw.text((int(wid/3-w/2)-100, 800), dest_us, font = font)

    w, h = draw.textsize(dest_them, font = font)
    draw.text((int(2*wid/3-w/2)+100, 800), dest_them, font = font)

    trademark = 'this action was performed automatically by a bot (created by @Juiced_Box)'
    font = ImageFont.truetype('font.ttf', 40)
    w, h = draw.textsize(trademark, font = font)
    draw.text(((1920-w)/2, 950), trademark, font = font, fill = (255,255,255, 120))
    background.save('res.png')
    return
    
def send_tweet(data):
    get_tweet(data)
    photo = open('res.png', 'rb')
    response = twitter.upload_media(media = photo)
    twitter.update_status(status = '', media_ids=[response['media_id']])
    print('tweet sent')
    return

def check_log():
    coc_data = requests.get(main_api, headers = {'Authorization': 'Bearer %s' %coc_token}).json()
    war_end_time = coc_data['items'][0]['endTime']
    a = datetime.strptime(war_end_time, date_format)
    b = datetime.strptime(str(datetime.utcnow()), date_format2)
    war_end_ago = b - a
    print(war_end_ago)
    if (war_end_ago <= delta):
        send_tweet(coc_data['items'][0])
    return

sched = BlockingScheduler()
sched.add_job(check_log, 'interval', minutes = 5)
sched.start()
