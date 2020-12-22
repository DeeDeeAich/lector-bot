import helpers.bible_url
import helpers.date_expand

from discord import Embed
from bs4 import BeautifulSoup

import requests
import datetime


class ArmenianLectionary:
    def __init__(self):
        self.bible_version = "nrsv"


    def _build_url(self, dateobject):
        int_month  = {
            1  : 'january',
            2  : 'february',
            3  : 'march',
            4  : 'april',
            5  : 'may',
            6  : 'june',
            7  : 'july',
            8  : 'august',
            9  : 'september',
            10 : 'october',
            11 : 'november',
            12 : 'december'
        }

        url = 'https://vemkar.us/<year>/<month>/<day>/<monthname>-<day>-<year>'
        url = url.replace('<year>'     , str(dateobject.year))
        url = url.replace('<month>'    , str(dateobject.month))
        url = url.replace('<day>'      , str(dateobject.day))
        url = url.replace('<monthname>', str(int_month[dateobject.month]))
        return url


    def _request_data(self):
        today = datetime.date.today()

        url = self._build_url(today)

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
            'title'    : title,
            'readings' : readings
        }


    def build_embeds(self):
        data = self._request_data()
        # I need to add code here to catch if the data request failed

        title    = data['title']
        readings = data['readings']

        embed = Embed(title=title)

        today = datetime.date.today()
        url = self._build_url(today)
        
        embed.set_author(name='Armenian Lectionary', url='https://vemkar.us/category/lectionary')

        today = datetime.date.today()
        embed.description = helpers.date_expand.expand(today)
        
        temp = '\n'.join([
            helpers.bible_url.convert(reading, self.bible_version)
            for reading in readings
        ])
        embed.add_field(name='Readings', value=temp)

        return [embed]