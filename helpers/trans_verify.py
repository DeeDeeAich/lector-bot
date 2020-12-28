'''
These are derived from https://www.biblegateway.com/versions/
because that's the search engine used to generate Bible links
'''

# Books with Protestant OT & NT
with_ot_and_nt = [
    'kj21',     # 21st Century King James Version
    'asv',      # American Standard Version
    'amp',      # Amplified Bible
    'ampc',     # Amplified Bible, Classic Edition
    'brg',      # BRG Bible
    'csb',      # Christian Standard Bible
    'ceb',      # Common English Bible (with Apocrypha)
    'cjb',      # Complete Jewish Bible
    'cev',      # Contemporary English Version
    'darby',    # Darby Translation (DARBY)
                # Disciples’ Literal New Testament (DLNT) unavailible b/c only NT
    'dra',      # Douay-Rheims 1899 American Edition (with Apocrypha)
    'erv',      # Easy-to-Read Version
    'ehv',      # Evangelical Heritage Version
    'esv',      # English Standard Version
    'esvuk',    # English Standard Version Anglicised
    'exb',      # Expanded Bible
    'gnv',      # 1599 Geneva Bible 	
    'gw',       # GOD’S WORD Translation
    'gnt',      # Good News Translation (with Apocrypha)
    'hcsb',     # Holman Christian Standard Bible
    'icb',      # International Children’s Bible
    'isv',      # International Standard Version
                # J.B. Phillips New Testament (PHILLIPS) unavailable b/c only NT
    'jub',      # Jubilee Bible 2000
    'kjv',      # King James Version
    'akjv',     # Authorized (King James) Version
    'leb',      # Lexham English Bible
    'tlb',      # Living Bible
    'msg',      # The Message
    'mev',      # Modern English Version
                # Mounce Reverse Interlinear New Testament (MOUNCE) unavailable b/c only NT
    'nog',      # Names of God Bible
    'namre',    # New American Bible (Revised Edition)
    'nasb',     # New American Standard Bible
    'nasb1995', # New American Standard Bible 1995	
    'ncv',      # New Century Version
    'net',      # New English Translation
    'nirv',     # New International Reader's Version
    'niv',      # New International Version
    'nivuk',    # New International Version - UK
    'nkjv',     # New King James Version	
    'nlv',      # New Life Version (NLV)
    'nlt',      # New Living Translation	
                # New Matthew Bible (NMB) unavailable b/c only NT
    'nrsv',     # New Revised Standard Version (with Apocrypha)
    'nrsva',    # New Revised Standard Version, Anglicised (with Apocrypha)
    'nrsvace',  # New Revised Standard Version, Anglicised Catholic Edition
    'nrsvce',   # New Revised Standard Version Catholic Edition
                # New Testament for Everyone (NTE) unavailable b/c only NT
    'ojb',      # Orthodox Jewish Bible
    'tpt',      # The Passion Translation
                # Revised Geneva Translation (RGT) unavailable b/c only NT
    'rsv',      # Revised Standard Version (with Apocrypha)
    'rsvce',    # Revised Standard Version Catholic Edition
    'tlv',      # Tree of Life Version
    'voice',    # The Voice
    'web',      # World English Bible
                # Worldwide English (New Testament) (WE) unavailable b/c only NT
    'wyc',      # Wycliffe Bible (with Apocrypha)
    'ylt'       # Young's Literal Translation
]


# Subset of books with OT and NT that also have Deuterocanon/Apocrypha
with_septuagint_books = [
    'ceb',   # Common English Bible
    'dra',   # Douay-Rheims 1899 American Edition
    'gnt',   # Good News Translation
    'nrsv',  # New Revised Standard Version
    'nrsva', # New Revised Standard Version, Anglicised
    'rsv',   # Revised Standard Version
    'wyc'    # Wycliffe Bible
]


def verify(lect, trans):
    '''
    Given a lectionary (either armenian, catholic, orthodox, rcl)
    and a Bible translation code, returns a boolean indicating
    whether the translation can cover the lectionary
    '''
    
    lects = ['armenian', 'catholic', 'orthodox', 'rcl']

    if lect not in lects: return None

    if (lect in lects[:-1]) and (trans in with_septuagint_books):
        return True
    elif (lect == lects[-1]) and (trans in with_ot_and_nt):
        return True
    else:
        return False