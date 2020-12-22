import helpers.bible_url
import helpers.date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import datetime


homepage_url    = 'https://lectionary.library.vanderbilt.edu/daily.php'
rss_daily_url   = 'https://lectionary.library.vanderbilt.edu//feeds/lectionary-daily.xml'
rss_weekly_url  = 'https://lectionary.library.vanderbilt.edu//feeds/lectionary.xml'


class RevisedCommonLectionary:
    def __init__(self):
        self.bible_version = 'nasb'


    def _request_daily(self):
        r = requests.get(rss_daily_url)
        if r.status_code != 200: return {}
        
        raw      = r.text.replace('<![CDATA[','').replace(']]>','')
        soup     = BeautifulSoup(raw, 'html.parser')
        title    = soup.select_one('item > title').text
        readings = soup.select_one('item > description > a').text.split('; ')

        return {
            'title'    : title,
            'readings' : readings
        }
    

    def _request_weekly(self):
        r = requests.get(rss_weekly_url)
        if r.status_code != 200: return {}

        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.select_one('item > title').text
        readings = soup.select_one('item > description').text.split(' * ')

        return {
            'title'    : title,
            'readings' : readings
        }
    

    def build_embeds(self):
        '''
        Function to convert daily lectionary info to discord.py embed object
        '''
        weekday = datetime.datetime.today().weekday()

        if weekday == 6: # If today is Sunday

            data = self._request_weekly()
            # I need to add code here to catch if the data request failed

            title    = data['title']
            readings = data['readings']

            embed = Embed(title=data['title'])
            name, url = 'Revised Common Lectionary', 'https://lectionary.library.vanderbilt.edu/daily.php'
            embed.set_author(name=name, url=url)

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


        else: # If today is any other day of the week
        
            data = self._request_daily()
            # I need to add code here to catch if the data request failed

            title = data['title']
            readings = data['readings']

            embed = Embed(title=title)
            name, url = 'Revised Common Lectionary', 'https://lectionary.library.vanderbilt.edu/daily.php'
            embed.set_author(name=name,url=url)

            embed.description = '\n'.join([
                helpers.bible_url.convert(reading, self.bible_version)
                for reading in readings
            ])


        return [embed]