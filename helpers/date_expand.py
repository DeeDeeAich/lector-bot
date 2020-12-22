import datetime

suffixes = {'0':'th','1':'st','2':'nd','3':'rd','4':'th','5':'th','6':'th','7':'th','8':'th','9':'th'}

def expand(dateobject):
    '''Given a date object, returns a specially formatted string representing it w/ the weekday'''
    day = str(dateobject.day)[-1]
    suffix = suffixes[day]
    return dateobject.strftime(f'%A, %B %d{suffix}, %Y')

def expand_no_weekday(dateobject):
    '''Given a date object, returns a specially formatted string representing it w/o the weekday'''
    day = str(dateobject.day)[-1]
    suffix = suffixes[day]
    return dateobject.strftime(f'%B %d{suffix}, %Y')