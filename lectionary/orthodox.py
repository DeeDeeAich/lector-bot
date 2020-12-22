import helpers.bible_url
import helpers.date_expand

from discord import Embed
from bs4 import BeautifulSoup

import requests
import datetime


class OrthodoxLectionary:
    def __init__(self):
        self.bible_version = 'nrsv'
    

    def _build_url(self):
        '''
        The webservice that hosts the Orthodox Calendar works by accepting PHP
        requests where the date of the day you want is encoded as arguments in
        the URL. This helper method constructions a url for today's date.

        There is info here:
        https://www.holytrinityorthodox.com/calendar/doc/index.htm

        But I reverse engineered this javascript to find the exact url format:
        https://www.holytrinityorthodox.com/calendar/doc/examples/loadCalendar2.js
        '''

        url  = 'https://www.holytrinityorthodox.com/calendar/doc/examples/ppp.php'
        url += '?month=%m&today=%d&year=%Y&dt=1&header=1&lives=1&trp=1&scripture=1'
        return datetime.datetime.today().strftime(url)
    

    def _request_data(self):
        '''
        Helper method to fetch and scrape the webpage containing the calendar data.
        '''

        r = requests.get(self._build_url())
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

        # Readings Section - this is the tricky one
        lines = [
            item
            for item in soup.select_one('span[class="normaltext"]:nth-child(5)').text.split('\n')
            if item]
        
        refs = [
            item.text
            for item in soup.select('span[class="normaltext"]:nth-child(5) > a')]

        added_info = [
            line.replace(ref, '').strip()
            for line, ref in zip(lines, refs)]
        
        readings = {}
        for ref, info in zip(refs, added_info):
            readings[ref] = info

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

        data = self._request_data()
        # Add code to catch a failed data request

        title      = data['title']
        subtitles  = data['subtitles']
        saints     = data['saints']
        readings   = data['readings']
        troparions = data['troparions']

        embeds = []

        # Title Embed
        title_embed = Embed(title=title)
        name, url = 'Orthodox Calendar', 'https://www.holytrinityorthodox.com/calendar/'
        title_embed.set_author(name=name, url=url)
        title_embed.description = '\n'.join(subtitles)
        embeds.append(title_embed)
        
        # Saints Embed
        saints_embed = Embed(title='The Saints')
        saints_embed.description = '\n'.join(saints)
        embeds.append(saints_embed)

        # Readings Embed
        scripture_embed = Embed(title='The Scripture Readings')
        reading_lines = '\n'.join([
            f'{helpers.bible_url.convert(key,self.bible_version)} {readings[key]}'
            for key in readings.keys()
        ])
        scripture_embed.description = reading_lines
        embeds.append(scripture_embed)

        # Troparion Embed
        troparion_embed = Embed(title='Troparion')
        for saint in troparions.keys():
            troparion_embed.add_field(name=saint, value=troparions[saint], inline=False)
        embeds.append(troparion_embed)

        return embeds