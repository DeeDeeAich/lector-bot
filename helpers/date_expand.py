import datetime

suffixes = {'0':'th','1':'st','2':'nd','3':'rd','4':'th','5':'th','6':'th','7':'th','8':'th','9':'th'}

def expand(dateobject):
    '''Given a date object, returns a specially formatted string representing it w/ the weekday'''
    suffix = suffixes[str(dateobject.day)[-1]]
    return dateobject.strftime(f'%A, %B {dateobject.day}{suffix}, %Y')

def expand_no_weekday(dateobject):
    '''Given a date object, returns a specially formatted string representing it w/o the weekday'''
    suffix = suffixes[str(dateobject.day)[-1]]
    return dateobject.strftime(f'%B {dateobject.day}{suffix}, %Y')

def auto_expand(dateobject, text):
    '''
    If some text does not contain the weekday, generate a datestamp
    that *does* contain the weekday. If the text contains it, the
    datestamp should not contain it
    '''
    if dateobject.strftime('%A') not in text:
        return expand(dateobject)
    else:
        return expand_no_weekday(dateobject)