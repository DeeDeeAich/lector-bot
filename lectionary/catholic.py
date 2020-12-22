from helpers import bible_url
from helpers import date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import re
import datetime


class CatholicLectionary:
    def __init__(self):
        self.bible_version = 'nrsv'


    def _build_permalink(self):
        '''
        Helper method to build a permalink to today's reading based upon the
        website's URL structure
        '''
        return datetime.date.today().strftime('https://bible.usccb.org/bible/readings/%m%d%y.cfm')


    def _scrape_page(self, url, text):
        '''
        Helper method to scrape a daily reading page that is known not to
        simply be a list of links.
        '''

        soup           = BeautifulSoup(text, 'html.parser')
        title          = soup.title.text.replace(' | USCCB','')
        footer         = soup.select_one('h2 ~ p').text.strip()
        content_blocks = soup.select('.b-verse>div>div>div>div')

        # This could be a double nested list comprehenion but meh
        sections = {}
        for content_block in content_blocks:
            header = content_block.select_one('h3').text.strip()
            links = []
            for link in content_block.select('a'):
                # If .strip() is removed, we also catch sections that don't have Bible references
                if link.text.strip() != '':
                    link = link.text.strip().replace('.','').replace(u'\xa0',u' ')         
                    links.append(link)
            if links: sections[header] = ' or '.join(links)

        return {
            'url'      : url,
            'title'    : title,
            'sections' : sections,
            'footer'   : footer
        }
    

    def _request_data(self):
        '''
        Helper method that handles all the GET requests that are needed to get
        the pages that contain the appropriate lectionary info.
        '''

        permalink = self._build_permalink()

        r = requests.get(permalink)
        if r.status_code != 200: return {}

        soup = BeautifulSoup(r.text, 'html.parser')
        content_blocks = soup.select('.b-verse>div>div>div>div')

        # If the daily page is a standard readout
        if len(content_blocks) > 1:
            return [self._scrape_page(permalink, r.text)]

        # Otherwise, the daily page is a list of links to other pages
        # Each page is scraped for its own Discord embed
        base_url = 'https://bible.usccb.org'
        anchors = soup.select('div[class="content-body"]>ul>li>a')
        output = []
        for link in anchors:
            link = link['href']

            # If the link is relative, make it absolute
            if 'https://' != link[:8]:
                link = ''.join([base_url, link])

            r = requests.get(link)
            if r.status_code != 200: return {}
            output.append(self._scrape_page(link, r.text))

        return output


    def _build_bible_link(self, reference):
        return bible_url.convert(self.expand_books(reference), self.bible_version)


    def build_embeds(self):
        '''
        Helper method to construct a list of Discord embeds based upon the
        data scraped from the daily readings webpages
        '''
        today = datetime.date.today()
        pages = self._request_data()

        embeds = []

        # For each of the pages that was scraped
        for page in pages:
            url      = page['url']
            title    = page['title']
            sections = page['sections']
            footer   = page['footer']
            
            embed = Embed(title=title)
            embed.set_author(name='Catholic Lectionary',url=url)
            embed.set_footer(text=footer)

            # If the weekday name ('Monday', 'Tuesday', etc.) is not in the title
            if today.strftime('%A') not in title:
                embed.description = date_expand.expand(today)
            else: embed.description = date_expand.expand_no_weekday(today)

            # For each lectionary section, ex: Reading 1, Responsorial Psalm, Reading 2, Alleluia, Gospel
            for key in sections.keys():
                # Generate a list of possible readings
                verse_options = sections[key].split(' or ')

                if len(verse_options) == 1: # If there was only one reading reference block in this section
                    result = re.search(r'(.*) \(cited in (.*)\)', verse_options[0])
                    if result: # Deals with cases that look like "Isaiah 61:1 (cited in Luke 4:18)"
                        link = f'{self._build_bible_link(result.group(1))} (cited in {self._build_bible_link(result.group(2))})'
                    else:
                        link = self._build_bible_link(verse_options[0])
                    embed.add_field(name=key, value=link, inline=False)
                
                else:
                    links = ' or\n'.join([
                        self._build_bible_link(reference)
                        for reference in verse_options])
                    embed.add_field(name=key, value=links, inline=False)
            
            # Build a single embed for each page
            embeds.append(embed)

        return embeds
    

    def expand_books(self, reference):
        substitutions = {
            'GN'     : 'Genesis',
            'EX'     : 'Exodus',
            'LV'     : 'Leviticus',
            'NM'     : 'Numbers',
            'DT'     : 'Deuteronomy',

            'Jos'    : 'Joshua',
            'JGS'    : 'Judges',
            'RU'     : 'Ruth',
            '1 SM'   : '1 Samuel',
            '2 SM'   : '2 Samuel',
            '1 KGS'  : '1 Kings',
            '2 KGS'  : '2 Kings',
            '1 CHR'  : '1 Chronicles',
            '2 CHR'  : '2 Chronicles',
            'EZR'    : 'Ezra',
            'NEH'    : 'Nehemiah',

            'TB'     : 'Tobit',
            'JDT'    : 'Judith',
            'EST'    : 'Esther',
            '1 MC'   : '1 Maccabees',
            '2 MC'   : '2 Maccabees',

            'JB'     : 'Job',
            'PS'     : 'Psalm',
            'PRV'    : 'Proverbs',
            'ECCL'   : 'Ecclesiastes',
            'SG'     : 'Song of Songs',
            'WIS'    : 'Wisdom',
            'SIR'    : 'Sirach',

            'IS'     : 'Isaiah',
            'JER'    : 'Jeremiah',
            'LAM'    : 'Lamentations',
            'BAR'    : 'Baruch',
            'EZ'     : 'Ezekiel',
            'DN'     : 'Daniel',
            'HOS'    : 'Hosea',
            'JL'     : 'Joel',
            'AM'     : 'Amos',
            'OB'     : 'Obadiah',
            'JON'    : 'Jonah',
            'MI'     : 'Micah',
            'NA'     : 'Nahum',
            'HB'     : 'Habakkuk',
            'ZEP'    : 'Zephaniah',
            'HG'     : 'Haggai',
            'ZEC'    : 'Zachariah',
            'MAL'    : 'Malachi',

            'MT'     : 'Matthew',
            'MK'     : 'Mark',
            'LK'     : 'Luke',
            'JN'     : 'John',

            'ACTS'   : 'Acts',

            'ROM'    : 'Romans',
            '1 COR'  : '1 Corinthians',
            '2 COR'  : '2 Corinthians',
            'GAL'    : 'Galatians',
            'EPH'    : 'Ephesians',
            'PHIL'   : 'Philippians',
            'COL'    : 'Colossians',
            '1 THES' : '1 Thessalonians',
            '2 THES' : '2 Thessalonians',
            '1 TM'   : '1 Timothy',
            '2 TM'   : '2 Timothy',
            'TI'     : 'Titus',
            'PHLM'   : 'Philemon',
            'HEB'    : 'Hebrews',

            'JAS'    : 'James',
            '1 PT'   : '1 Peter',
            '2 PT'   : '2 Peter',
            '1 JN'   : '1 John',
            '2 JN'   : '2 John',
            '3 JN'   : '3 John',
            'JUDE'   : 'Jude',
            'RV'     : 'Revelation'
        }
    
        reference = reference.upper()

        for original in substitutions.keys():
            reference = reference.replace(original, substitutions[original])
        
        return reference
    

'''
The _request_data() function will break down on certain Christian holidays
because the format of the website changes. The Christman lectionary for has
readings for different times of the day. I didn't try to implement the fix
yet because it will involve more than just scraping a single page. It will
have to finding links, following them, and make additional get requests.

UPDATE: I've almost got this working for days that have multiple sets of
readings. The only issues I'm experiencing come from a strange source -
malformed title strings. Perhaps I'll scrape the title from the title HTML
element instead of the body.

UPDATE: Scraping from the title element worked as a one-liner. :P
'''