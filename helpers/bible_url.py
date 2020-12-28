import re


def convert(reference, bible_version, view_mode):
    '''
    Converts an individual Bible reference & version into a neat Markdown link
    '''
    anchor = reference

    reference = reference.replace('(','').replace(')','')
    reference = reference.replace('[','').replace(']','')

    # Get rid of letter subreferences in verses
    # Ex: '1 Samuel 2:8ABCD' is cleaned to '1 Samuel 2:8'
    results = re.findall(r'[0-9]+([a-zA-Z]+)', reference)
    for result in results:
        reference = reference.replace(result, '')
        anchor    = anchor.replace(result, result.lower())
    
    reference = reference.replace(' ', '+').lower()

    if view_mode == 'normal'  : tail = ''
    elif view_mode == 'print' : tail = '&interface=print'
    else                      : tail = ''
    
    return f'[{anchor}](https://www.biblegateway.com/passage/?search={reference}&version={bible_version}{tail})'


def html_convert(text, bible_version, view_mode):
    '''
    Converts a string with anchored Bible references to Markdown

    In: "God creates everything in <a>Genesis 1:1</a>"
    Out: "God creates everything in [Genesis 1:1](https://www.blahblah.com)
    '''
    matches = re.findall(r'(<a>([^<>]*)<\/a>)', text)
    for match in matches:
        text = text.replace(match[0], convert(match[1], bible_version, view_mode))
    
    return text