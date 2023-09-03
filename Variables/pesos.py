import string
import json
import redis

r_pesos = redis.StrictRedis(host='localhost', port=6379, db=12)

# Carga de datos del algoritmo (pesos) de la BD Redis.
keys = r_pesos.keys()

pesos_delete_def = None
pesos_insert_def = None
pesos_subs_def = None
pesos_transp_def = None
contextos = None

if b'pesos_delete' in keys:
    pesos_delete_def = json.loads(r_pesos.get(b'pesos_delete'))
else:
    pesos_delete_def = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_delete_def[ch] = 1

if b'pesos_insert' in keys:
    pesos_insert_def = json.loads(r_pesos.get(b'pesos_insert'))
else:
    pesos_insert_def = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_insert_def[ch] = 1

if b'pesos_subs' in keys:
    pesos_subs_def = json.loads(r_pesos.get(b'pesos_subs'))
else:
    pesos_subs_def = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_subs_def['#_' + ch1 + '#_' + ch2] = 1

if b'pesos_transp' in keys:
    pesos_transp_def = json.loads(r_pesos.get(b'pesos_transp'))
else:
    pesos_transp_def = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_transp_def['#_' + ch1 + '#_' + ch2] = 1

if b'contextos' in keys:
    contextos = json.loads(r_pesos.get(b'contextos'))
else:
    contextos = {}