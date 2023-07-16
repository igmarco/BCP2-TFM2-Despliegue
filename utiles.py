import json
import re

def decode_json(introducido):
    lista = introducido.decode('utf-8').replace('\'', '"')
    return json.loads(lista)

def recortar_cadena(cadena, ini, long):
    cadena_tokenizada = re.sub(' +', ' ',
                               re.sub(';|,|\.|¿|\?|¡|!', ' ', cadena).strip()
                               # texto
                               ).split()
    cadena_final = ''
    cadena_recortada = ''

    for i in range(len(cadena_tokenizada)):
        if i not in range(ini, ini + long + 1):
            cadena_final += cadena_tokenizada[i] + ' '
        else:
            cadena_recortada += cadena_tokenizada[i] + ' '

    return cadena_final[:-1], cadena_recortada[:-1]