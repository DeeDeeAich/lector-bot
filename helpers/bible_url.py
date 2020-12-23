import re


def convert(reference:str, version:str):
    '''
    Converts a given Bible reference & version into a neat Markdown link
    '''
    anchor = reference
    results = re.findall(r'[0-9]+([a-zA-Z]+)', reference)

    for result in results:
        reference = reference.replace(result, '')
        anchor    = anchor.replace(result, result.lower())
    
    reference = reference.replace(' ', '+')
    return f'[{anchor}](https://www.biblegateway.com/passage/?search={reference}&version={version}&interface=print)'

'''
convert() will produce broken links if it is given a reference that is outside
the given version. I plan on solving this when I implement a system to make
sure a specific Bible version encommpasses all the books a given lectionary
could potentially throw at it.
'''