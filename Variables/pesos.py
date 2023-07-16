import string
import json
import redis

r_pesos = redis.StrictRedis(host='localhost', port=6379, db=12)

# Carga de datos del algoritmo (pesos) de la BD Redis.
keys = r_pesos.keys()

if b'pesos_delete' in keys:
    pesos_delete_def = json.loads(r_pesos.get(b'pesos_delete'))
if b'pesos_insert' in keys:
    pesos_insert_def = json.loads(r_pesos.get(b'pesos_insert'))
if b'pesos_subs' in keys:
    pesos_subs_def = json.loads(r_pesos.get(b'pesos_subs'))
if b'pesos_transp' in keys:
    pesos_transp_def = json.loads(r_pesos.get(b'pesos_transp'))
if b'contextos' in keys:
    contextos = json.loads(r_pesos.get(b'contextos'))