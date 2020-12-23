import helpers.bible_url
import helpers.date_expand

from discord import Embed
from discord import Colour

from bs4 import BeautifulSoup

import requests
import datetime


class ArmenianLectionary:
    def __init__(self):
        self.bible_version = "nrsv"


    def _build_url(self):
        today = datetime.datetime.today()
        return today.strftime(f'https://vemkar.us/%B-{today.day}-%Y')


    def _request_data(self):
        url = self._build_url()

        r = requests.get(url)
        if r.status_code != 200: return {}

        soup     = BeautifulSoup(r.text, 'html.parser')
        title    = soup.select('h2')[1].text.replace('\n',' ')
        readings = soup.select_one('h4[style]').text
        
        substitutions = {
            'II ' : '2 ',
            'I '  : '1 '
        }

        for original in substitutions.keys():
            readings = readings.replace(original, substitutions[original])

        readings = readings.split('\n')

        return {
            'url'      : url,
            'title'    : title,
            'readings' : readings
        }


    def build_embeds(self):
        try:
            data     = self._request_data()
            url      = data['url']
            title    = data['title']
            readings = data['readings']
        except KeyError:
            return []

        embed = Embed(title=title)
        embed.set_author(name='Armenian Lectionary', url=url)

        today = datetime.date.today()
        embed.description = helpers.date_expand.expand(today)
        
        temp = '\n'.join([
            helpers.bible_url.convert(reading, self.bible_version)
            for reading in readings
        ])
        embed.add_field(name='Readings', value=temp)

        return [embed]