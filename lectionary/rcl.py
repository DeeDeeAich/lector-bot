import helpers.bible_url
import helpers.date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import datetime


homepage_url    = 'https://lectionary.library.vanderbilt.edu/daily.php'


class RevisedCommonLectionary:
    def __init__(self):
        self.bible_version = 'nasb'


    def _request_data(self):
        today_sunday = (datetime.datetime.today().weekday() == 6)

        if today_sunday:
            url = 'https://lectionary.library.vanderbilt.edu//feeds/lectionary.xml'
        else:
            url = 'https://lectionary.library.vanderbilt.edu//feeds/lectionary-daily.xml'
        
        r = requests.get(url)
        if r.status_code != 200: return {}

        if today_sunday: raw = r.text
        else:            raw = r.text.replace('<![CDATA[','').replace(']]>','')

        soup  = BeautifulSoup(raw, 'html.parser')
        title = soup.select_one('item > title').text

        if today_sunday:
            readings = soup.select_one('item > description').text.split(' * ')
        else:
            readings = soup.select_one('item > description > a').text.split('; ')

        return {
            'title'        : title,
            'readings'     : readings,
            'today_sunday' : today_sunday
        }


    def build_embeds(self):
        '''
        Function to convert daily lectionary info to discord.py embed object
        '''

        data = self._request_data()
        # I need to add code here to catch if the data request failed

        title        = data['title']
        readings     = data['readings']
        today_sunday = data['today_sunday']

        embed = Embed(title=title)
        name, url = 'Revised Common Lectionary', 'https://lectionary.library.vanderbilt.edu/daily.php'
        embed.set_author(name=name, url=url)

        if today_sunday:
            lines = []
            
            for reading in readings:
                options = reading.split(' or ')

                if len(options) == 1:
                    link = helpers.bible_url.convert(reading,self.bible_version)
                else:
                    link = ' or '.join([
                        helpers.bible_url.convert(option, self.bible_version)
                        for option in options
                        ])
                
                lines.append(link)

            embed.description = "\n".join(lines)
        
        else:
            embed.description = '\n'.join([
                helpers.bible_url.convert(reading, self.bible_version)
                for reading in readings
            ])

        return [embed]