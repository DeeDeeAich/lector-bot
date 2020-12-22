import re
from time import sleep

def convert(reference:str, version:str):
    reference = shorten(reference)
    base = 'https://www.biblegateway.com/passage/?search=<reference>&version=<version>&interface=print'
    link = base.replace('<reference>',reference.replace(' ','+')).lower().replace('ab','')
    link = link.replace('<version>',version)
    return f'[{reference}]({link})'

'''
to_bible_url() will produce broken links if it is given a reference that is
outside the given version. I plan on solving this when I implement a system
to make sure a specific Bible version encommpasses all the books any
lectionary could throw at it.
'''

def shorten(reference:str):
    '''
    Many times, a reference will be written weird like 'John 3:1-16, 17'
    This function will try to collapse it to look more like 'John 3:1-17'

    This code is bad
    '''

    while '  ' in reference: reference = reference.replace(' ',' ')

    pattern = r"(([0-9]+) *, *([0-9]+))"

    matches = re.findall(pattern,reference)
    for match in matches:
        if int(match[1]) + 1 == int(match[2]):
            reference = reference.replace(match[0], f'{match[1]}-{match[2]}')
    
    if matches:
        reference = reference[::-1]
        matches = re.findall(pattern,reference)
        for match in matches:
            if int(match[1]) - 1 == int(match[2]):
                reference = reference.replace(match[0], f'{match[1]}-{match[2]}')
        reference = reference[::-1]

    pattern = r"(([0-9]+)(-[0-9]+)+-([0-9]+))"
    matches = re.findall(pattern,reference)
    for match in matches: reference = reference.replace(match[0], f'{match[1]}-{match[3]}')

    return reference