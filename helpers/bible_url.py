import re


def convert(reference):
    '''
    Converts an individual Bible reference & version into a neat Markdown link
    '''
    anchor = reference

    reference = reference.replace('(','').replace(')','').replace('[','').replace(']','')

    # Get rid of letter subreferences in verses
    # Ex: '1 Samuel 2:8ABCD' is cleaned to '1 Samuel 2:8'
    temp    = reference
    pattern = r'([0-9]+)([a-zA-Z]+)'
    match   = re.search(pattern, temp)
    while match:
        reference = reference.replace(match.group(0), match.group(1))
        temp      = temp[match.span()[1]:]
        match     = re.search(pattern, temp)
    
    reference = reference.replace(' ', '+')
    
    return f'[{anchor}](https://www.biblegateway.com/passage/?search={reference})'


def html_convert(text):
    '''
    Converts a string with anchored Bible references to Markdown

    In: "God creates everything in <a>Genesis 1:1</a>"
    Out: "God creates everything in [Genesis 1:1](https://www.example.com)"
    '''
    matches = re.findall(r'(<a>([^<>]*)<\/a>)', text)
    for match in matches:
        text = text.replace(match[0], convert(match[1]))
    
    return text