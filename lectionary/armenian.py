from helpers import bible_url
from helpers import date_expand

from discord import Embed
from discord import Colour

from bs4 import BeautifulSoup

import requests
import datetime


class ArmenianLectionary:
    def __init__(self):
        self.regenerate_data()
    

    def clear_data(self):
        self.url      = ''
        self.title    = ''
        self.desc     = ''
        self.readings = ''


    def regenerate_data(self):
        today = datetime.date.today()
        self.url = today.strftime(f'https://vemkar.us/%Y/%m/%d/%B-{today.day}-%Y')

        r = requests.get(self.url)
        if r.status_code != 200:
            self.clear_data()
            return
        
        soup = BeautifulSoup(r.text, 'html.parser')

        self.title = soup.select('h2')[1].text
        self.desc  = date_expand.expand(datetime.date.today())

        readings = soup.select_one('h4[style]').text

        substitutions = {'III ':'3 ','II ':'2 ','I ':'1 '}
        for original in substitutions.keys():
            readings = readings.replace(original, substitutions[original])
        
        readings = readings.split('\n')
        readings = [f'<a>{reading}</a>' for reading in readings]
        readings = '\n'.join(readings)

        self.readings = readings


    def build_embeds(self):
        embed = Embed(title=self.title)
        embed.set_author(name='Armenian Lectionary', url=self.url)
        embed.description = self.desc
        embed.add_field(name='Readings', value=bible_url.html_convert(self.readings))

        return [embed]