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
        self.url       = ''
        self.title     = ''
        self.desc      = ''
        self.readings  = ''
        self.notes_url = ''
        self.ready     = False


    def regenerate_data(self):
        today = datetime.date.today()
        self.url = today.strftime(f'https://vemkar.us/%Y/%m/%d/%B-{today.day}-%Y')
        
        try:
            r = requests.get(self.url)
            if r.status_code != 200:
                self.clear_data()
                return
        except:
            self.clear_data()
            return
        
        soup = BeautifulSoup(r.text, 'html.parser')

        self.title = soup.select('h2')[1].text
        self.desc  = date_expand.auto_expand(datetime.date.today(), self.title)

        readings = soup.select_one('h4[style]').text

        substitutions = {'III ':'3 ','II ':'2 ','I ':'1 ','Azariah':'Prayer of Azariah'}
        for original in substitutions.keys():
            readings = readings.replace(original, substitutions[original])
        
        readings = readings.split('\n')
        readings = [f'<a>{reading}</a>' for reading in readings]

        self.readings = '\n'.join(readings)

        # Get pages with additional lectionary notes, if they exist
        try:
            r = requests.get(today.strftime(f'https://vemkar.us/%B-{today.day}-%Y'))
            if r.status_code != 200:
                self.clear_data()
                return
        except:
            self.clear_data()
            return
        
        # If there was no redirect, this is a unique resource
        if (len(r.history) == 0):
            soup = BeautifulSoup(r.text, 'html.parser')
            self.notes_url = soup.select_one("p[class='attachment']>a")['href']
        # If there was a redirect, everything was already scraped
        else:
            self.notes_url = ''
        
        self.ready = True


    def build_embeds(self):
        if not self.ready: return []

        title = self.title + '\n' + self.desc
        embed = Embed(title=title)
        embed.set_author(name='Armenian Lectionary', url=self.url)

        temp = bible_url.html_convert(self.readings)
        if self.notes_url != '': temp += f"\n\n*[Notes]({self.notes_url})"
        embed.description = temp

        return [embed]