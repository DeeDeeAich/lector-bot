import helpers.bible_url
import helpers.date_expand

from discord import Embed
from bs4 import BeautifulSoup

import requests
import re
import datetime


class OrthodoxLectionary:
    def __init__(self):
        self.bible_version = 'nrsv'
  

    def _build_url(self):
        today = datetime.datetime.today()
        return f'https://www.holytrinityorthodox.com/calendar/calendar.php?month={today.month}&today={today.day}&year={today.year}&dt=1&header=1&lives=1&trp=1&scripture=1'


    def _request_data(self):
        '''
        Helper method to scrape the webpage containing the calendar data.
        '''

        url = self._build_url()

        r = requests.get(url)
        if r.status_code != 200: return {}

        soup = BeautifulSoup(r.text, 'html.parser')

        # Title and subtitle
        title     = soup.select_one('span[class="dataheader"]').text
        a         = soup.select_one('span[class="headerheader"]').text
        b         = soup.select_one('span[class="headerfast"]').text
        subtitles = [a.replace(b,''), b.strip()]
        
        # Saint Section
        saints = [
            item
            for item in soup.select_one('span[class="normaltext"]').text.split('\n')
            if item]

        # Readings Section
        readings = soup.select_one('span[class="normaltext"]:nth-child(5)')
        readings = [str(item) for item in readings.contents]
        readings = ''.join(readings)
        readings = readings.replace('\n','')
        readings = readings.split('<br/>')
        readings = [reading for reading in readings if reading != '']

        for index, reading in enumerate(readings):
            match = re.search(r'<a.*>(.*)<\/a>', reading)
            if match:
                # 'tag' looks like '<a>Matthew 5:11</a>'
                # 'ref' looks like 'Matthew 5:11'
                tag, ref = match.group(0), match.group(1)
                link = helpers.bible_url.convert(ref, self.bible_version)
                readings[index] = reading.replace(tag, link)

        # Troparion Section
            # keys represent the saint name and tone number
        keys = [item.text for item in soup.select('p > b:first-child')]
        values = [item.text for item in soup.select('span[class="normaltext"] > p')]
        values = [value.replace(key, '') for key, value in zip(keys, values)]

        keys   = [key.replace('\n','').replace('\r','').replace(' —','') for key in keys]
        values = [value.replace('\n','').replace('\r','') for value in values]

        troparions = {}
        for key, value in zip(keys, values):
            troparions[key] = value

        return {
            'url'        : url,
            'title'      : title,
            'subtitles'  : subtitles,
            'saints'     : saints,
            'readings'   : readings,
            'troparions' : troparions
        }
    

    def build_embeds(self):
        '''
        "Public" function to construct a list of Discord Embeds representing
        the calendar data.
        '''        
        try:
            data       = self._request_data()
            url        = data['url']
            title      = data['title']
            subtitles  = data['subtitles']
            saints     = data['saints']
            readings   = data['readings']
            troparions = data['troparions']
        except KeyError:
            return []
        
        embeds = []

        # Title Embed
        title_embed = Embed(title=title)
        name        = 'Orthodox Calendar'
        title_embed.set_author(name=name, url=url)
        title_embed.description = '\n'.join(subtitles)
        embeds.append(title_embed)
        
        # Saints Embed
        saints_embed = Embed(title='The Saints')
        saints_embed.description = '\n'.join(saints)
        embeds.append(saints_embed)

        # Readings Embed
        scripture_embed = Embed(title='The Scripture Readings')
        scripture_embed.description = '\n'.join(readings)
        embeds.append(scripture_embed)

        # Troparion Embed
        troparion_embed = Embed(title='Troparion')
        for saint in troparions.keys():
            troparion_embed.add_field(name=saint, value=troparions[saint], inline=False)
        embeds.append(troparion_embed)

        return embeds