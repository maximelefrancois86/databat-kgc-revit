from re import sub
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def camel_case(s:str):
    return sub(r"(_|-)+", " ", s).title().replace(" ", "")