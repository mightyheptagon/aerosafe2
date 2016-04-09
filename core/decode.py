# -*- coding: utf-8 -*-
import re
def decodeword(word):
    # fixing decoding problem
    word = word.replace('’', "'")
    word = word.replace('‘', "'")
    word = word.replace('º', "")
    word = word.replace('.', "")
    word = word.replace('“', '"')
    word = word.replace('”', '"')
    word = word.replace('´', "'")
    word = re.sub(r'[^\x00-\x7F]+',' ', word) # final attack!!
    try:
        result = word.decode('utf-8').encode('utf-8', "ignore")
        return result
    except:
        try:
            result = word.decode('cp1252').encode('utf-8', "ignore")
            return result
        except:
            try:
                result = word.decode('latin').encode('utf-8', "ignore")
                return result
            except:
                return word
