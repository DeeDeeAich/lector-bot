import helpers.bible_url
import helpers.date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import re
import datetime


class RevisedCommonLectionary:
    def __init__(self):
        self.bible_version = 'nasb'


    def _scrape_text_php(self, url):
        '''
        Instead of providing a list of references, the daily readings page
        might link to another page containing a list of readings. This
        helper method scrapes from that.
        '''
        r = requests.get(url)
        if r.status_code != 200: return []

        soup = BeautifulSoup(r.text, 'html.parser')

        readings = soup.select_one('div[class="texts_msg_bar"]:first-child>ul')
        readings = readings.text.replace('\n','')

        links = readings.replace(' and ',';').replace(' or ',';').replace('\xa0\xa0•\xa0', ';').split(';')

        for link in links:
            readings = readings.replace(link, helpers.bible_url.convert(link))
        
        readings = readings.split('\xa0\xa0•\xa0')

        return readings


    def _request_data(self):
        url = 'https://lectionary.library.vanderbilt.edu/daily.php'

        r = requests.get(url)
        if r.status_code != 200: return {}

        soup = BeautifulSoup(r.text, 'html.parser')
        lines = soup.select('ul[class="daily_day"]>li')

        # Generate the regex pattern matching today's date
        today = datetime.datetime.today()
        check = today.strftime(f'%B.* {today.day}[^0-9].*%Y')

        got_today = False
        output = {'year_letter': soup.select_one('[id="main_text"]>h2').text[-1]}

        for line in lines:
            line = [str(item) for item in line.contents]
            line = ''.join(line).replace('&amp;','&')

            # If the entry is not for today
            if not re.search(check, line):
                if got_today: break
                continue
            got_today = True

            # Listings that have an explicit list of readings
            match = re.search(r'<strong>(.*)<\/strong>: *<a href="http:.*>(.*)<\/a>', line)
            if match:
                readings = match.group(2).split("; ")
                readings = [helpers.bible_url.convert(reading) for reading in readings]
                output[''] = readings
                break

            # Listings that have semi-continuous and complementary readings
            match = re.search(r'<strong>(.*)<\/strong>: <br\/>Semi-continuous: <a.*>(.*)<\/a><br\/>Complementary: <a.*>(.*)<\/a>', line)
            if match:
                output['Semi-continuous'] = [helpers.bible_url.convert(reading) for reading in match.group(2).split("; ")]
                output['Complementary']   = [helpers.bible_url.convert(reading) for reading in match.group(3).split("; ")]
                break

            # Listings that link to another page for the readings
            match = re.search(r'<strong>(.*)<\/strong>: *<strong><a href="(.*)">(.*)<\/a><\/strong>', line)
            if match:
                fetched_readings = self._scrape_text_php(f'https://lectionary.library.vanderbilt.edu/{match.group(2)}')
                if fetched_readings == {}: return {}
                output[match.group(3)] = self._scrape_text_php(f'https://lectionary.library.vanderbilt.edu/{match.group(2)}')
        
        return output



    def build_embeds(self):
        '''
        Function to convert daily lectionary info to discord.py Embed
        '''
        data = self._request_data()
        if data == {}: return []

        date_string = helpers.date_expand.expand(datetime.datetime.today())
        embed = Embed(title=f'Daily Readings for {date_string} (Year {data["year_letter"]})')
        name, url = 'Revised Common Lectionary', 'https://lectionary.library.vanderbilt.edu/daily.php'
        embed.set_author(name=name, url=url)

        for key in data.keys():
            if key == '':
                embed.description = '\n'.join(data[''])
                break
            elif key == 'year_letter':
                continue
            else:
                readings = '\n'.join(data[key])
                embed.add_field(name=key, value=readings)

        return [embed]