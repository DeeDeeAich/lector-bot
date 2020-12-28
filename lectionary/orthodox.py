from helpers import bible_url
from helpers import date_expand

from discord import Embed
from bs4 import BeautifulSoup

import requests
import re
import datetime


class OrthodoxLectionary:
    def __init__(self):
        self.regenerate_data()
  

    def clear_data(self):
        self.url       = ''
        self.title     = ''
        self.subtitles = []
        self.saints    = []
        self.readings  = []
        self.troparion = {}


    def regenerate_data(self):
        today = datetime.datetime.today()
        self.url = f'https://www.holytrinityorthodox.com/calendar/calendar.php?month={today.month}&today={today.day}&year={today.year}&dt=1&header=1&lives=1&trp=1&scripture=1'

        r = requests.get(self.url)
        if r.status_code != 200:
            self.clear_data()
            return
        
        soup = BeautifulSoup(r.text, 'html.parser')

        # Title & subtitles
        self.title     = soup.select_one('span[class="dataheader"]').text
        a              = soup.select_one('span[class="headerheader"]').text
        b              = soup.select_one('span[class="headerfast"]').text
        self.subtitles = [a.replace(b,''), b.strip()]

        # Saints
        self.saints = [
            item
            for item in soup.select_one('span[class="normaltext"]').text.split('\n')
            if item
        ]

        # Readings
        readings = soup.select_one('span[class="normaltext"]:nth-child(5)')
        readings = [str(item) for item in readings.contents]
        readings = ''.join(readings)
        readings = readings.replace('\n','')
        readings = readings.replace('<br/>', '\n')
        if readings[-1] == '\n': readings = readings[:-1]

        matches = re.findall(r'(<a.*>([^<>]*)<\/a>)', readings)
        for match in matches:
            readings = readings.replace(match[0], f'<a>{match[1]}</a>')
        
        self.readings = readings

        # Troparion
            # keys represent saint/tone
            # values represent troparion contents
        keys = [item.text for item in soup.select('p > b:first-child')]
        values = [item.text for item in soup.select('span[class="normaltext"] > p')]
        values = [value.replace(key, '') for key, value in zip(keys, values)]

        keys   = [key.replace('\n','').replace('\r','').replace(' —','') for key in keys]
        values = [value.replace('\n','').replace('\r','') for value in values]

        self.troparion = {}
        for key, value in zip(keys, values):
            self.troparion[key] = value
    

    def build_embeds(self, bible_version, view_mode):
        '''
        "Public" function to construct a list of Discord Embeds representing
        the calendar data.
        '''
        
        embeds = []

        # Title & Subtitles Embed
        embed = Embed(title=self.title)
        embed.set_author(name='Orthodox Calendar', url=self.url)
        embed.description = '\n'.join(self.subtitles)
        embeds.append(embed)
        
        # Saints Embed
        embed = Embed(title='The Saints')
        embed.description = '\n'.join(self.saints)
        embeds.append(embed)

        # Readings Embed
        embed = Embed(title='The Scripture Readings')
        embed.description = bible_url.html_convert(self.readings, bible_version, view_mode)
        embeds.append(embed)

        # Troparion Embed
        embed = Embed(title='Troparion')
        for saint in self.troparion.keys():
            embed.add_field(name=saint, value=self.troparion[saint], inline=False)
        embeds.append(embed)

        return embeds