import redis
import json
from collections import Counter
import csv
import string

import numpy as np
import pandas as pd

from ModeloDeDominio.Region import Region

from Recorrido.recorrer_BD_secuencial import mejores_resultados_recorrer_BD_secuencial

from DamerauLevenshtein.DL_training import damerau_levenshtein_distance_training

def inicializar_entrenamiento(r_pesos):
    """
    Almacena en la BD Redis correspondiente a las correspondencias del algoritmo de comparación de cadenas valores por
    defecto.

    Parameters
    ----------
    r_pesos : object
        conexión con la BD Redis correspondiente a los pesos y correspondencias
    """

    pesos_delete_correspondencias = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_delete_correspondencias[ch] = 0

    pesos_insert_correspondencias = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_insert_correspondencias[ch] = 0

    pesos_subs_correspondencias = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_subs_correspondencias['#_' + ch1 + '#_' + ch2] = 0

    pesos_transp_correspondencias = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_transp_correspondencias['#_' + ch1 + '#_' + ch2] = 0

    contextos_registrados = {}

    uso_letras = {}

    r_pesos.set('pesos_delete_correspondencias', json.dumps(pesos_delete_correspondencias))
    r_pesos.set('pesos_insert_correspondencias', json.dumps(pesos_insert_correspondencias))
    r_pesos.set('pesos_subs_correspondencias', json.dumps(pesos_subs_correspondencias))
    r_pesos.set('pesos_transp_correspondencias', json.dumps(pesos_transp_correspondencias))
    r_pesos.set('contextos_registrados', json.dumps(contextos_registrados))
    r_pesos.set('uso_letras', json.dumps(uso_letras))


def inicializar_pesos(r_pesos):
    """
    Almacena en la BD Redis correspondiente a los pesos del algoritmo de comparación de cadenas valores por
    defecto.

    Parameters
    ----------
    r_pesos : object
        conexión con la BD Redis correspondiente a los pesos y correspondencias
    """

    pesos_delete_def = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_delete_def[ch] = 1

    pesos_insert_def = {}
    for ch in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        pesos_insert_def[ch] = 1

    pesos_subs_def = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_subs_def['#_' + ch1 + '#_' + ch2] = 1

    pesos_transp_def = {}
    for ch1 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
        for ch2 in string.ascii_letters + string.digits + string.punctuation + 'ñÑáÁéÉíÍóÓúÚüÜºª ':
            pesos_transp_def['#_' + ch1 + '#_' + ch2] = 1

    contextos = {}

    r_pesos.set('pesos_delete', json.dumps(pesos_delete_def))
    r_pesos.set('pesos_insert', json.dumps(pesos_insert_def))
    r_pesos.set('pesos_subs', json.dumps(pesos_subs_def))
    r_pesos.set('pesos_transp', json.dumps(pesos_transp_def))
    r_pesos.set('contextos', json.dumps(contextos))


def entrenar_pesos(ruta_fichero, r_BD, r_pesos, umbral_tolerancia=0.5):
    """
    En base a las direcciones contenidas en un fichero CSV con la información sobre las cadenas de las direcciones más
    sus correspondientes campos reales, se entrenan las correspondencias bajo una tolerancia mínima

    Parameters
    ----------
    ruta_fichero : str
        ruta del fichero CSV que contiene la información sobre la dirección
    r_BD : object
        conexión con la BD Redis correspondiente a los registros T1
    r_pesos : object
        conexión con la BD Redis correspondiente a los pesos y correspondencias
    umbral_tolerancia : float
        valor entre 0 y 1 que representa el umbral de la tolerancia ante la confianza de los resultados
    """

    pesos_delete_correspondencias = {}
    pesos_insert_correspondencias = {}
    pesos_subs_correspondencias = {}
    pesos_transp_correspondencias = {}
    contextos_registrados = {}
    uso_letras = {}

    # Carga de datos T2 de CSV.
    cadenas = pd.read_csv(ruta_fichero, header=0, sep=',')

    # Carga de datos del algoritmo (pesos) de la BD Redis.
    keys = r_pesos.keys()

    if b'pesos_delete_correspondencias' in keys:
        pesos_delete_correspondencias = json.loads(r_pesos.get(b'pesos_delete_correspondencias'))
    if b'pesos_insert_correspondencias' in keys:
        pesos_insert_correspondencias = json.loads(r_pesos.get(b'pesos_insert_correspondencias'))
    if b'pesos_subs_correspondencias' in keys:
        pesos_subs_correspondencias = json.loads(r_pesos.get(b'pesos_subs_correspondencias'))
    if b'pesos_transp_correspondencias' in keys:
        pesos_transp_correspondencias = json.loads(r_pesos.get(b'pesos_transp_correspondencias'))
    if b'contextos_registrados' in keys:
        contextos_registrados = json.loads(r_pesos.get(b'contextos_registrados'))
    if b'uso_letras' in keys:
        uso_letras = json.loads(r_pesos.get(b'uso_letras'))

    for i_row, row in cadenas.iterrows():
        print('Cadena ' + str(i_row+1) + '/' + str(cadenas.shape[0]) + ':', row['cadena'])
        resultados, mejores_resultados = mejores_resultados_recorrer_BD_secuencial(row['cadena'],
                                                                                   r_BD,
                                                                                   comentarios=False)
        # print(mejores_resultados)

        for resultado in mejores_resultados:

            if resultado[0].comprobar(r_BD):
                confianza = resultado[0].confianza()
                print('Resultado con confianza del ' + str(int(confianza*100)) + '%')

                if confianza >= umbral_tolerancia:
                    print('Actualizando pesos y contextos...')

                    for clave, valor in resultado[0].__dict__.items():
                        if type(valor) == Region and valor.match is not None and valor.nombre == row[valor.estructura]:
                            resultado, \
                            pesos_delete_correspondencias_tmp, \
                            pesos_insert_correspondencias_tmp, \
                            pesos_subs_correspondencias_tmp, \
                            pesos_transp_correspondencias_tmp, \
                            contextos_registrados_tmp, \
                            uso_letras_tmp = damerau_levenshtein_distance_training(valor.nombre, valor.match)

                            # Actualizando pesos...
                            estructuras_pesos = [(pesos_delete_correspondencias_tmp, pesos_delete_correspondencias),
                                                 (pesos_insert_correspondencias_tmp, pesos_insert_correspondencias),
                                                 (pesos_subs_correspondencias_tmp, pesos_subs_correspondencias),
                                                 (pesos_transp_correspondencias_tmp, pesos_transp_correspondencias)]

                            for estructura_pesos in estructuras_pesos:
                                for elemento in estructura_pesos[0]:
                                    estructura_pesos[1][elemento] += estructura_pesos[0][str(elemento)]

                            # Actualizando contextos...
                            for contexto in contextos_registrados_tmp:
                                if contexto in contextos_registrados:
                                    contextos_registrados[contexto].extend(contextos_registrados_tmp[contexto])
                                else:
                                    contextos_registrados[contexto] = contextos_registrados_tmp[contexto]

                            # Actualizando uso de letras...
                            for letra in uso_letras_tmp:
                                if letra in uso_letras:
                                    uso_letras[letra] += uso_letras_tmp[letra]
                                else:
                                    uso_letras[letra] = uso_letras_tmp[letra]

                else:
                    print('Cadena desechada por resultado con baja confianza.')

            else:
                print('Cadena desechada por resultado erróneo.')

    # Almacenando información.
    r_pesos.set('pesos_delete_correspondencias', json.dumps(pesos_delete_correspondencias))
    r_pesos.set('pesos_insert_correspondencias', json.dumps(pesos_insert_correspondencias))
    r_pesos.set('pesos_subs_correspondencias', json.dumps(pesos_subs_correspondencias))
    r_pesos.set('pesos_transp_correspondencias', json.dumps(pesos_transp_correspondencias))
    r_pesos.set('contextos_registrados', json.dumps(contextos_registrados))
    r_pesos.set('uso_letras', json.dumps(uso_letras))

def entrenar_pesos_fila(fila_dict, r_BD, r_pesos, umbral_tolerancia=0.5):
    """
    En base a la dirección contenida en un diccionario con la información sobre la cadena de la dirección más
    sus correspondientes campos reales, se entrenan las correspondencias bajo una tolerancia mínima

    Parameters
    ----------
    fila_dict : dict
        diccionario contenedor de la cadena de la dirección y de los valores correspondientes a las regiones reales
        de la direccion
    r_BD : object
        conexión con la BD Redis correspondiente a los registros T1
    r_pesos : object
        conexión con la BD Redis correspondiente a los pesos y correspondencias
    umbral_tolerancia : float
        valor entre 0 y 1 que representa el umbral de la tolerancia ante la confianza de los resultados
    """

    general_path = 'DatosCSV/cargas.csv'
    tmp_path = 'DatosCSV/carga_temp.csv'

    with open(general_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([fila_dict['cadena'],
                         fila_dict['estado'],
                         fila_dict['ca'],
                         fila_dict['provincia'],
                         fila_dict['comarca'],
                         fila_dict['municipio'],
                         fila_dict['nivel'],
                         fila_dict['tipovia'],
                         fila_dict['via'],
                         fila_dict['numero'],
                         fila_dict['codPostal'],
                         fila_dict['nombrepropio']])
    with open(tmp_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['cadena','estado','ca','provincia','comarca','municipio',
                         'nivel','tipovia','via','numero','codPostal','nombrepropio',])
        writer.writerow([fila_dict['cadena'],
                         fila_dict['estado'],
                         fila_dict['ca'],
                         fila_dict['provincia'],
                         fila_dict['comarca'],
                         fila_dict['municipio'],
                         fila_dict['nivel'],
                         fila_dict['tipovia'],
                         fila_dict['via'],
                         fila_dict['numero'],
                         fila_dict['codPostal'],
                         fila_dict['nombrepropio'],
                         ])

    entrenar_pesos(tmp_path, r_BD, r_pesos, umbral_tolerancia)


def actualizar_pesos(r_pesos):
    """
    Se recogen los valores de las correspondencias y se actualizan en base a ellos los valores de los pesos del
    algoritmo

    Parameters
    ----------
    r_pesos : object
        conexión con la BD Redis correspondiente a los pesos y correspondencias
    """

    pesos_delete = {}
    pesos_insert = {}
    pesos_subs = {}
    pesos_transp = {}
    contextos = {}

    inicializar_pesos(r_pesos)

    pesos_delete_correspondencias = {}
    pesos_insert_correspondencias = {}
    pesos_subs_correspondencias = {}
    pesos_transp_correspondencias = {}
    contextos_registrados = {}
    uso_letras = {}

    # Carga de datos del algoritmo (pesos) de la BD Redis.
    keys = r_pesos.keys()

    if b'pesos_delete_correspondencias' in keys:
        pesos_delete_correspondencias = json.loads(r_pesos.get(b'pesos_delete_correspondencias'))
    if b'pesos_insert_correspondencias' in keys:
        pesos_insert_correspondencias = json.loads(r_pesos.get(b'pesos_insert_correspondencias'))
    if b'pesos_subs_correspondencias' in keys:
        pesos_subs_correspondencias = json.loads(r_pesos.get(b'pesos_subs_correspondencias'))
    if b'pesos_transp_correspondencias' in keys:
        pesos_transp_correspondencias = json.loads(r_pesos.get(b'pesos_transp_correspondencias'))
    if b'contextos_registrados' in keys:
        contextos_registrados = json.loads(r_pesos.get(b'contextos_registrados'))
    if b'uso_letras' in keys:
        uso_letras = json.loads(r_pesos.get(b'uso_letras'))

    rango_uso_letras = np.array(list(uso_letras.values()))
    max_uso_letras, min_uso_letras = np.max(rango_uso_letras), np.min(rango_uso_letras)

    # Delete
    rango_delete = np.array(list(pesos_delete_correspondencias.values()))
    max_delete, min_delete = np.max(rango_delete), np.min(rango_delete)

    for letra in pesos_delete_correspondencias:
        if pesos_delete_correspondencias[letra] > 0:
            pesos_delete[letra] = 1.5 - ((pesos_delete_correspondencias[letra] - min_delete)/(max_delete - min_delete))/((uso_letras[letra] - min_uso_letras)/(max_uso_letras - min_uso_letras))
        else:
            pesos_delete[letra] = 1

    # Insert
    rango_insert = np.array(list(pesos_insert_correspondencias.values()))
    max_insert, min_insert = np.max(rango_insert), np.min(rango_insert)

    for letra in pesos_insert_correspondencias:
        if pesos_insert_correspondencias[letra] > 0:
            pesos_insert[letra] = 1.5 - ((pesos_insert_correspondencias[letra] - min_insert)/(max_insert - min_insert))/((uso_letras[letra] - min_uso_letras)/(max_uso_letras - min_uso_letras))
        else:
            pesos_insert[letra] = 1

    # Substitution
    max_subs, min_subs = 0,1000000

    for comb in pesos_subs_correspondencias:
        if len(comb) == 4:
            if pesos_subs_correspondencias[comb] > max_subs:
                max_subs = pesos_subs_correspondencias[comb]
            elif pesos_subs_correspondencias[comb] < min_subs:
                min_subs = pesos_subs_correspondencias[comb]

    for comb in pesos_subs_correspondencias:
        duple = np.array(comb.split('#_'))[1:]

        # Si es entre dos letras
        if len(duple[0]) == 1 and len(duple[1] == 1):
            if pesos_subs_correspondencias[comb] > 0:
                pesos_subs[comb] = 1.5 - ((pesos_subs_correspondencias[comb] - min_subs) / (max_subs - min_subs)) / (((uso_letras[duple[0]] - min_uso_letras) / (max_uso_letras - min_uso_letras) + (uso_letras[duple[1]] - min_uso_letras) / (max_uso_letras - min_uso_letras)) / 2)
            else:
                pesos_subs[comb] = 1

        # Si es entre dos strings o entre letra y string
        else:
            if pesos_subs_correspondencias[comb] > 0:
                pesos_subs[comb] = 1.5 - ((pesos_subs_correspondencias[comb] - min_subs) / (max_subs - min_subs))
            else:
                pesos_subs[comb] = 1

    # Transposition
    rango_transp = np.array(list(pesos_transp_correspondencias.values()))
    max_transp, min_transp = np.max(rango_transp), np.min(rango_transp)

    for comb in pesos_transp_correspondencias:
        duple = np.array(comb.split('#_'))

        if pesos_transp_correspondencias[comb] > 0:
            pesos_transp[comb] = 1.5 - ((pesos_transp_correspondencias[comb] - min_transp)/(max_transp - min_transp))/(((uso_letras[duple[0]] - min_uso_letras)/(max_uso_letras - min_uso_letras) + (uso_letras[duple[1]] - min_uso_letras)/(max_uso_letras - min_uso_letras))/2)
        else:
            pesos_transp[comb] = 1

    # Context
    max_rep_context = 0

    for comb in contextos_registrados:
        conteo = Counter(contextos_registrados[comb])
        for contexto in conteo.keys():
            if conteo[contexto] > max_rep_context:
                max_rep_context = conteo[contexto]

    for comb in contextos_registrados:
        conteo = Counter(contextos_registrados[comb])
        for contexto in conteo.keys():
            if conteo[contexto] > int(max_rep_context/2):
                if comb in contextos:
                    contextos[comb].append((contexto, conteo[contexto]/max_rep_context))
                else:
                    contextos[comb] = [(contexto, conteo[contexto]/max_rep_context)]

    # Almacenando información.
    r_pesos.set('pesos_delete', json.dumps(pesos_delete))
    r_pesos.set('pesos_insert', json.dumps(pesos_insert))
    r_pesos.set('pesos_subs', json.dumps(pesos_subs))
    r_pesos.set('pesos_transp', json.dumps(pesos_transp))
    r_pesos.set('contextos', json.dumps(contextos))


if __name__ == '__main__':
    ruta_fichero = 'T2_procesados/Prueba.csv'

    # Establecimiento de las conexiones con Redis.
    r_BD = redis.StrictRedis(host='localhost', port=6379, db=11)
    r_pesos = redis.StrictRedis(host='localhost', port=6379, db=12)

    inicializar_entrenamiento(r_pesos)

    entrenar_pesos(ruta_fichero, r_BD, r_pesos)

    actualizar_pesos(r_pesos)

