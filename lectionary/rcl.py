from helpers import bible_url
from helpers import date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import re
import datetime


class RevisedCommonLectionary:
    def __init__(self):
        self.regenerate_data()
    

    def clear_data(self):
        self.url         = ''
        self.title       = ''
        self.year_letter = ''
        self.sections    = {}


    def _explode_reference_list(self, text):
        '''
        This helper method takes in a common-separated list of Bible
        references, and explodes it into a list where each reference
        is independent
        
        For instance, 'John 1; Acts 7; 8' will get exploded to
        ['John 1', 'Acts 7', 'Acts 8']
        '''
        pattern = r'(([0-9] )?[a-zA-Z]+[0-9 \-\:]+); ([0-9]+[^ ])'

        expander = re.search(pattern, text)
        while expander:
            replacement = f'{expander.group(1)}<semicolon> {expander.group(3)}'
            text = text.replace(expander.group(0), replacement)
            expander = re.search(pattern, text)
        
        return [item.replace('<semicolon>', ';') for item in text.split('; ')]


    def regenerate_data(self):
        self.url = 'https://lectionary.library.vanderbilt.edu/daily.php'
        r = requests.get(self.url)
        if r.status_code != 200:
            self.clear_data()
            return

        soup = BeautifulSoup(r.text, 'html.parser')

        self.year_letter = soup.select_one('[id="main_text"]>h2').text[-1]
        self.title = f'Daily Readings for {date_expand.expand(datetime.datetime.today())} (Year {self.year_letter})'

        lines = soup.select('ul[class="daily_day"]>li')

        # Generate the regex pattern matching today's date
        today = datetime.date.today()
        check = today.strftime(f'%B.* {today.day}[^0-9].*%Y')
        
        self.sections = {}
        got_today = False
        for line in lines:
            line = [str(item) for item in line.contents]
            line = ''.join(line).replace('&amp;','&')

            # If the entry is not for today
            if not re.search(check, line):
                if got_today: break
                continue
            got_today = True

            # Listings with explicit list of readings
            match = re.search(r'<strong>(.*)<\/strong>: *<a href="http:.*>(.*)<\/a>', line)
            if match:
                readings = self._explode_reference_list(match.group(2))
                readings = '\n'.join([f'<a>{reading}</a>' for reading in readings])
                self.sections[''] = readings
                break
                
            # Listings with semi-continuous & complementary 
            match = re.search(r'<strong>(.*)<\/strong>: <br\/>Semi-continuous: <a.*>(.*)<\/a><br\/>Complementary: <a.*>(.*)<\/a>', line)
            if match:
                self.sections['Semi-continuous'] = ''.join([
                    f'<a>{reading}</a>'
                    for reading in self._explode_reference_list(match.group(2))
                ])
            
                self.sections['Complementary'] = ''.join([
                    f'<a>{reading}</a>'
                    for reading in self._explode_reference_list(match.group(3))
                ])

                break
                
            # Listings that link to another page for the readings
            match = re.search(r'<strong>(.*)<\/strong>: *<strong><a href="(.*)">(.*)<\/a><\/strong>', line)
            if match:
                fetched = self._scrape_text_php(f'https://lectionary.library.vanderbilt.edu/{match.group(2)}')
                self.sections[match[3]] = fetched
    

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
            readings = readings.replace(link, f'<a>{link}</a>')
        
        readings = readings.replace('\xa0\xa0•\xa0', '\n')

        return readings


    def build_embeds(self, bible_version, view_mode):
        '''
        Function to convert daily lectionary info to discord.py Embed
        '''
        embed = Embed(title=self.title)
        embed.set_author(name='Revised Common Lectionary', url=self.url)

        for key in self.sections.keys():
            if key == '':
                embed.description = bible_url.html_convert(self.sections[''], bible_version, view_mode)
            else:
                value = bible_url.html_convert(self.sections[key], bible_version, view_mode)
                embed.add_field(name=key, value=value, inline=False)

        return [embed]