from helpers import bible_url
from helpers import date_expand

from bs4 import BeautifulSoup
from discord import Embed

import requests
import re
import datetime


class CatholicPage:
    '''
    A class that takes in the link, and possibly the raw HTML, for a Catholic
    readings page, scrapes the key info, and uses this as its attributes
    '''

    def __init__(self, url, source_text=None):
        self.url = url

        if source_text is None:
            try:
                r = requests.get(url)
                if r.status_code != 200:
                    self.clear_data()
                    return
            except:
                self.clear_data()
                return
            
            source_text = r.text

        soup = BeautifulSoup(source_text, 'html.parser')

        self.title  = soup.title.text.replace(' | USCCB','')
        self.footer = soup.select_one('h2 ~ p').text.strip()

        today = datetime.date.today()
        self.desc = date_expand.auto_expand(today, self.title)

        blocks = soup.select('.b-verse>div>div>div>div')
        self.sections = {}
        
        for block in blocks:
            header = block.select_one('h3').text.strip()

            if (header == ''):
                # There is a glitch on the website where the 'Gospel' label
                # will be missing from the page. None of the other labels
                # appear to do that for whatever reason. It cannot be left
                # empty because Discord embed field names must be non-empty.
                header = 'Gospel'

            lines = []
            for link in block.select('a'):
                link = link.text.strip()
                if link == '': continue
                link = link.replace('.','').replace(u'\xa0',u' ')
                link = link.replace(' and ',', ').replace(' AND ',', ')
                
                # If a reference in the Responsorial Psalm section does not
                # include "Ps", insert it at the beginning
                if (header == 'Responsorial Psalm') and (link[0] in list('0123456789')):
                    link = 'Ps ' + link

                lines.append(link)
            
            if len(lines) > 0:
                for index, link in enumerate(lines):
                    match = re.search(r'(.*) \(cited in (.*)\)', lines[index])
                    if match:
                        # Deals with cases that look like "Isaiah 61:1 (cited in Luke 4:18)"
                        first  = self._clean_ref(match.group(1))
                        second = self._clean_ref(match.group(2))
                        lines[index] = f'<a>{first}</a> (cited in <a>{second}</a>)'
                    elif link.startswith('See '):
                        new = lines[index][4:]
                        lines[index] = f'See <a>{self._clean_ref(new)}</a>'
                    elif link.startswith('Cf '):
                        new = lines[index][3:]
                        lines[index] = f'Cf. <a>{self._clean_ref(new)}</a>'
                    else:
                        lines[index] = f'<a>{self._clean_ref(lines[index])}</a>'
                    
                lines = ' or\n'.join(lines)
                self.sections[header] = lines
        
        self.ready = True


    def clear_data(self):
        self.url      = ''
        self.title    = ''
        self.desc     = ''
        self.sections = {}
        self.footer   = ''
        self.ready    = False


    def _clean_ref(self, reference):
        substitutions = {
            'GN'     : 'Genesis',
            'EX'     : 'Exodus',
            'LV'     : 'Leviticus',
            'NM'     : 'Numbers',
            'DT'     : 'Deuteronomy',

            'JOS'    : 'Joshua',
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
            if f'{original} ' in reference:
                reference = reference.replace(original, substitutions[original])
                break
        
        return reference


class CatholicLectionary:
    def __init__(self):
        self.regenerate_data()
    

    def clear_data(self):
        self.pages = []
        self.ready = False


    def regenerate_data(self):
        '''
        Helper method that handles all the GET requests that are needed to get
        the pages that contain the appropriate lectionary info.
        '''
        permalink = datetime.date.today().strftime('https://bible.usccb.org/bible/readings/%m%d%y.cfm')
        
        try:
            r = requests.get(permalink)
            if r.status_code != 200:
                self.clear_data()
                return
        except:
            self.clear_data()
            return


        soup = BeautifulSoup(r.text, 'html.parser')
        blocks = soup.select('.b-verse>div>div>div>div')

        # If the daily page is a standard readout
        if len(blocks) > 1:
            page = CatholicPage(permalink, r.text)
            if page.ready:
                self.pages = [page]
        else:
            # Otherwise, the daily page is a list of links to other pages
            # Each page gets its own embed
            base_url = 'https://bible.usccb.org'
            anchors = soup.select('div[class="content-body"]>ul>li>a')
            self.pages = []
            for link in anchors:
                link = link['href']

                # If the link is relative, make it absolute
                if 'https://' != link[:8]:
                    link = ''.join([base_url, link])

                page = CatholicPage(link)
                if page.ready:
                    self.pages.append(CatholicPage(link))
                else:
                    self.clear_data()
                    return
        
        self.ready = True


    def build_embeds(self):
        '''
        Helper method to construct a list of Discord embeds based upon the
        data scraped from the daily readings webpages
        '''
        if not self.ready: return []

        embeds = []

        # For each page that was scraped
        for page in self.pages:
            embed = Embed(title=page.title)
            embed.set_author(name='Catholic Lectionary', url=page.url)
            embed.set_footer(text=page.footer)
            embed.description = page.desc

            # For each lectionary section on the page
            # Ex: Reading 1, Responsorial Psalm, Reading 2, Alleluia, Gospel
            for header in page.sections.keys():
                value = bible_url.html_convert(page.sections[header])
                embed.add_field(name=header, value=value, inline=False)
            
            # An embed for each page
            embeds.append(embed)

        return embeds