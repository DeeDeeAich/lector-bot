import re


def convert(reference:str, version:str, interface:bool):
    '''
    Converts a given Bible reference & version into a neat Markdown link
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

    if interface: tail = '&interface=print'
    else:         tail = ''
    
    return f'[{anchor}](https://www.biblegateway.com/passage/?search={reference}&version={version}{tail})'