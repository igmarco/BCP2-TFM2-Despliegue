import numpy as np
import re

from ModeloDeDominio.Direccion import Direccion
from ModeloDeDominio.Region import Region, RegionVacia

from Variables.estructura import estructuras, superestructura, subestructura, pasos_opcionales, pasos_iniciales, origen

from DamerauLevenshtein.DL import comparacion_palabras, damerau_levenshtein_similarity

from utiles import recortar_cadena

def recorrer_BD_completa_secuencial(cadena_origen, r, comentarios=True):
    """
    Se recorre la BD contrastando los registros con la cadena objetivo, devolviendo las direcciones coincidentes.
    El proceso se ejecuta de forma secuencial.

    Parameters
    ----------
    cadena_origen : str
        cadena con la dirección objetivo
    r : object
        conexión con la BD Redis con los registros T1
    comentarios : bool
        permite especificar si se desea mostrar comentarios informativos del proceso
    """

    texto_tokenizado = re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ', cadena_origen).strip()).split()

    direcciones_posibles = {'estado': set(),
                            'ca': set(),
                            'provincia': set(),
                            'comarca': set(),
                            'municipio': set(),
                            'nivel': set(),
                            'via': set(),
                            'numero': set(),
                            'codPostal': set()}
    nombres_evaluados = {'estado': {},
                         'ca': {},
                         'provincia': {},
                         'comarca': {},
                         'municipio': {},
                         'nivel': {},
                         'tipovia': {},
                         'via': {},
                         'numero': {},
                         'codPostal': {},
                         'nombrepropio': {}}

    direcciones = {(Direccion(), cadena_origen), }
    tolerancia = 0.75

    for estr in estructuras:

        if comentarios:
            print(estr + ':')

        regiones = []
        for region in Region.regiones(estr, r):
            regiones.append(region)

        if comentarios:
            print(list(regiones))
            print()

        direcciones_nuevas = set()

        for region in regiones:
            if region.nombre not in nombres_evaluados[estr]:
                for direccion in direcciones:

                    nombres = region.nombres()

                    mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}

                    for candidato in nombres:

                        longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)
                        resultados = np.zeros((len(texto_tokenizado), len(longitudes)))

                        texto_tokenizado = re.sub(' +', ' ',
                                                  re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split()

                        resultados_candidato = comparacion_palabras(texto_tokenizado,
                                                                    candidato,
                                                                    longitudes,
                                                                    damerau_levenshtein_similarity,
                                                                    resultados)

                        for row in range(len(texto_tokenizado) - min(longitudes)):
                            for column in range(len(longitudes)):
                                if row + column + min(longitudes) < len(texto_tokenizado) and resultados_candidato[
                                    row, column] > mejor_resultado['Similaridad']:
                                    mejor_resultado = {'Variante': candidato,
                                                       'Inicio': row,
                                                       'Longitud': column + len(candidato.split()) - 1,
                                                       'Similaridad': float(resultados_candidato[row, column])}

                    nombres_evaluados[estr][region.nombre] = mejor_resultado

            if nombres_evaluados[estr][region.nombre]['Similaridad'] >= tolerancia:

                for direccion in direcciones:
                    direcc = direccion[0].__copy__()
                    direcc.__dict__[estr] = region
                    direcc.__dict__[estr].confianza = \
                        nombres_evaluados[estr][region.nombre]['Similaridad']

                    nueva_cadena, cadena_restante = recortar_cadena(direccion[1],
                                                                    nombres_evaluados[estr][
                                                                        region.nombre]['Inicio'],
                                                                    nombres_evaluados[estr][
                                                                        region.nombre]['Longitud'])

                    direcc.__dict__[estr].match = cadena_restante

                    direcciones_nuevas.add((direcc, nueva_cadena))

        direcciones = direcciones_nuevas if len(
            direcciones_nuevas) > 0 else direcciones

    direcciones_posibles[origen] = direcciones




def recorrer_BD_secuencial(cadena_origen, r, comentarios=True):
    """
    Se recorre la BD contrastando los registros con la cadena objetivo, devolviendo las direcciones coincidentes.
    El proceso se ejecuta de forma secuencial.

    Parameters
    ----------
    cadena_origen : str
        cadena con la dirección objetivo
    r : object
        conexión con la BD Redis con los registros T1
    comentarios : bool
        permite especificar si se desea mostrar comentarios informativos del proceso
    """

    texto_tokenizado = re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ', cadena_origen).strip()).split()

    direcciones_posibles = {'estado': set(),
                            'ca': set(),
                            'provincia': set(),
                            'comarca': set(),
                            'municipio': set(),
                            'nivel': set(),
                            'via': set(),
                            'numero': set(),
                            'codPostal': set()}
    nombres_evaluados = {'estado': {},
                         'ca': {},
                         'provincia': {},
                         'comarca': {},
                         'municipio': {},
                         'nivel': {},
                         'tipovia': {},
                         'via': {},
                         'numero': {},
                         'codPostal': {},
                         'nombrepropio': {}}

    direcciones_iniciales = {(Direccion(), cadena_origen), }
    tolerancia = 0.75

    for estructura_inicial in pasos_iniciales:

        if comentarios:
            print(estructura_inicial + ':')

        regiones = []
        for region in Region.regiones(estructura_inicial, r):
            regiones.append(region)

        if comentarios:
            print(list(regiones))
            print()

        direcciones_iniciales_nuevas = set()

        for region in regiones:
            if region.nombre not in nombres_evaluados[estructura_inicial]:
                for direccion in direcciones_iniciales:

                    nombres = region.nombres()

                    mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}

                    for candidato in nombres:

                        longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)
                        resultados = np.zeros((len(texto_tokenizado), len(longitudes)))

                        texto_tokenizado = re.sub(' +', ' ',
                                                  re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split()

                        resultados_candidato = comparacion_palabras(texto_tokenizado,
                                                                    candidato,
                                                                    longitudes,
                                                                    damerau_levenshtein_similarity,
                                                                    resultados)

                        for row in range(len(texto_tokenizado) - min(longitudes)):
                            for column in range(len(longitudes)):
                                if row + column + min(longitudes) < len(texto_tokenizado) and resultados_candidato[row, column] > mejor_resultado['Similaridad']:
                                    mejor_resultado = {'Variante': candidato,
                                                       'Inicio': row,
                                                       'Longitud': column + len(candidato.split()) - 1,
                                                       'Similaridad': float(resultados_candidato[row, column])}

                    nombres_evaluados[estructura_inicial][region.nombre] = mejor_resultado

            if nombres_evaluados[estructura_inicial][region.nombre]['Similaridad'] >= tolerancia:

                for direccion in direcciones_iniciales:
                    direcc = direccion[0].__copy__()
                    direcc.__dict__[estructura_inicial] = region
                    direcc.__dict__[estructura_inicial].confianza = \
                        nombres_evaluados[estructura_inicial][region.nombre]['Similaridad']

                    nueva_cadena, cadena_restante = recortar_cadena(direccion[1],
                                                                    nombres_evaluados[estructura_inicial][
                                                                        region.nombre]['Inicio'],
                                                                    nombres_evaluados[estructura_inicial][
                                                                        region.nombre]['Longitud'])

                    direcc.__dict__[estructura_inicial].match = cadena_restante

                    direcciones_iniciales_nuevas.add((direcc, nueva_cadena))

        direcciones_iniciales = direcciones_iniciales_nuevas if len(
            direcciones_iniciales_nuevas) > 0 else direcciones_iniciales

    direcciones_posibles[origen] = direcciones_iniciales

    if comentarios:
        print('Direcciones posibles (' + origen + ')')
        print(direcciones_posibles[origen])
        print()

    estructura_actual = origen
    recorrido_completo = False

    while not recorrido_completo:

        estructura_actual = subestructura[estructura_actual]

        if comentarios:
            print(estructura_actual + ':')

        regiones = {}
        for superestruct in superestructura[estructura_actual]:
            for superdireccion in direcciones_posibles[superestruct]:
                for direccion in superdireccion[0].posibles_subdirecciones(estructura_actual, r):
                    if direccion.__dict__[estructura_actual] not in regiones:
                        regiones[direccion.__dict__[estructura_actual]] = [(direccion, superdireccion[1])]
                    else:
                        regiones[direccion.__dict__[estructura_actual]].append((direccion, superdireccion[1]))

        if comentarios:
            print(list(regiones))
            print()

        alguno_guardado = False

        for region in regiones:

            if region.nombre not in nombres_evaluados[estructura_actual]:

                nombres = region.nombres()
                mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}

                for candidato in nombres:
                    resultados_candidato = []
                    longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)

                    for direccion in regiones[region]:
                        texto_tokenizado = re.sub(' +', ' ',
                                                  re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split()
                        resultados = np.zeros((len(texto_tokenizado), len(longitudes)))

                        resultados_candidato.append((comparacion_palabras(texto_tokenizado,
                                                                          candidato,
                                                                          longitudes,
                                                                          damerau_levenshtein_similarity,
                                                                          resultados),
                                                     len(texto_tokenizado)))

                    for resultados in resultados_candidato:
                        for row in range(len(resultados[0])):
                            for column in range(len(resultados[0][0])):
                                if row + column + min(longitudes) < resultados[1] and resultados[0][row, column] > \
                                        mejor_resultado['Similaridad']:
                                    mejor_resultado = {'Variante': candidato,
                                                       'Inicio': row,
                                                       'Longitud': column + len(candidato.split()) - 1,
                                                       'Similaridad': float(resultados[0][row, column])}

                nombres_evaluados[estructura_actual][region.nombre] = mejor_resultado

            if nombres_evaluados[estructura_actual][region.nombre]['Similaridad'] >= tolerancia:

                for direccion in regiones[region]:
                    direcc = direccion[0].__copy__()
                    direcc.__dict__[estructura_actual] = region
                    direcc.__dict__[estructura_actual].confianza = nombres_evaluados[estructura_actual][region.nombre][
                        'Similaridad']

                    cadena_recortada, cadena_restante = recortar_cadena(direccion[1],
                                                                        nombres_evaluados[estructura_actual][
                                                                            region.nombre]['Inicio'],
                                                                        nombres_evaluados[estructura_actual][
                                                                            region.nombre]['Longitud'])

                    direcc.__dict__[estructura_actual].match = cadena_restante

                    direcciones_posibles[estructura_actual].add((direcc, cadena_recortada))
                alguno_guardado = True

        if not alguno_guardado:
            if estructura_actual != origen and estructura_actual not in pasos_opcionales:
                super_regiones_vacias = True
                for superestruct in superestructura[estructura_actual]:
                    for direccion in direcciones_posibles[superestruct]:
                        if type(direccion[0].__dict__[superestruct]) != RegionVacia:
                            super_regiones_vacias = False
                if not super_regiones_vacias:

                    # Hacemos el reset de todas las superestructuras y sacamos las nuevas regiones.
                    regiones = {}

                    for superestruct in superestructura[estructura_actual]:
                        direcciones_posibles_super_nuevas = set()
                        for direccion_conservada in direcciones_posibles[superestruct]:
                            subcadena_arrancada = ''
                            for sup in superestructura[estructura_actual]:
                                if direccion_conservada[0].__dict__[sup].match is not None:
                                    subcadena_arrancada += direccion_conservada[0].__dict__[sup].match + ' '
                                direccion_conservada[0].__dict__[sup] = RegionVacia(sup)

                            if direccion_conservada[0] not in direcciones_posibles_super_nuevas:
                                direcciones_posibles_super_nuevas.add((direccion_conservada[0],
                                                                       direccion_conservada[
                                                                           1] + ' ' + subcadena_arrancada[:-1]))
                        direcciones_posibles[superestruct] = direcciones_posibles_super_nuevas

                        for superdireccion in direcciones_posibles[superestruct]:
                            for direccion in superdireccion[0].posibles_subdirecciones(estructura_actual, r):
                                if direccion.__dict__[estructura_actual] not in regiones:
                                    regiones[direccion.__dict__[estructura_actual]] = [(direccion, superdireccion[1])]
                                else:
                                    regiones[direccion.__dict__[estructura_actual]].append(
                                        (direccion, superdireccion[1]))

                    if comentarios:
                        print('No se han encontrado coincidencias en ' + estructura_actual + '.')
                        print(estructura_actual + ' (generalización):')
                        print(list(regiones))
                        print()

                    alguno_guardado = False

                    for region in regiones:

                        # En este caso queremos que se evalúen con la parte de cadena anterior
                        # if region.nombre not in nombres_evaluados[estructura_actual]:

                        nombres = region.nombres()
                        mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}

                        for candidato in nombres:
                            resultados_candidato = []
                            longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)

                            for direccion in regiones[region]:
                                texto_tokenizado = re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ',
                                                                            direccion[1]).strip()).split()
                                resultados = np.zeros((len(texto_tokenizado), len(longitudes)))

                                resultados_candidato.append((comparacion_palabras(texto_tokenizado,
                                                                                  candidato,
                                                                                  longitudes,
                                                                                  damerau_levenshtein_similarity,
                                                                                  resultados),
                                                             len(texto_tokenizado)))

                            for resultados in resultados_candidato:
                                for row in range(len(resultados[0])):
                                    for column in range(len(resultados[0][0])):
                                        if row + column + min(longitudes) < resultados[1] and resultados[0][
                                            row, column] > \
                                                mejor_resultado['Similaridad']:
                                            mejor_resultado = {'Variante': candidato,
                                                               'Inicio': row,
                                                               'Longitud': column + len(candidato.split()) - 1,
                                                               'Similaridad': float(resultados[0][row, column])}

                        nombres_evaluados[estructura_actual][region.nombre] = mejor_resultado

                        if nombres_evaluados[estructura_actual][region.nombre]['Similaridad'] >= tolerancia:

                            for direccion in regiones[region]:
                                direcc = direccion[0].__copy__()
                                direcc.__dict__[estructura_actual] = region
                                direcc.__dict__[estructura_actual].confianza = \
                                    nombres_evaluados[estructura_actual][region.nombre][
                                        'Similaridad']

                                cadena_recortada, cadena_restante = recortar_cadena(direccion[1],
                                                                                    nombres_evaluados[
                                                                                        estructura_actual][
                                                                                        region.nombre][
                                                                                        'Inicio'],
                                                                                    nombres_evaluados[
                                                                                        estructura_actual][
                                                                                        region.nombre][
                                                                                        'Longitud'])

                                direcc.__dict__[estructura_actual].match = cadena_restante

                                direcciones_posibles[estructura_actual].add((direcc, cadena_recortada))

                            alguno_guardado = True

                # Es evidente que ahora la superregión será la general.
                if not alguno_guardado:
                    direcciones_posibles[estructura_actual] = set()
                    for superestruct in superestructura[estructura_actual]:
                        direcciones_posibles[estructura_actual] = (
                                direcciones_posibles[estructura_actual] | direcciones_posibles[superestruct])

            else:
                direcciones_posibles[estructura_actual] = set()
                for superestruct in superestructura[estructura_actual]:
                    direcciones_posibles[estructura_actual] = (
                            direcciones_posibles[estructura_actual] | direcciones_posibles[superestruct])

        if comentarios:
            print('Direcciones posibles (' + estructura_actual + ')')
            print(direcciones_posibles[estructura_actual])
            print()

        if estructura_actual not in subestructura:
            recorrido_completo = True

    return direcciones_posibles

def mejores_resultados_recorrer_BD_completa_secuencial(cadena_origen, r, comentarios=False):
    """
    Se obtienen los mejores resultados devueltos por recorrer_BD_secuencial.

    Parameters
    ----------
    cadena_origen : str
        cadena con la dirección objetivo
    r : object
        conexión con la BD Redis con los registros T1
    comentarios : bool
        permite especificar si se desea mostrar comentarios informativos del proceso
    """

    resultados = recorrer_BD_completa_secuencial(cadena_origen, r, comentarios)

    resultados_herentes = []

    for resultado in resultados['numero']:
        if resultado[0].comprobar(r):
            resultados_herentes.append(resultado)


    max_completitud = 0
    for resultado in resultados_herentes:
        max_completitud = max(max_completitud, resultado[0].completitud())

    max_confianza = 0
    for resultado in resultados_herentes:
        if resultado[0].completitud() == max_completitud:
            max_confianza = max(max_confianza, resultado[0].confianza())

    mejores_resultados = []
    for resultado in resultados_herentes:
        if resultado[0].completitud() == max_completitud and resultado[0].confianza() == max_confianza:
            mejores_resultados.append(resultado)

    return resultados, mejores_resultados


def mejores_resultados_recorrer_BD_secuencial(cadena_origen, r, comentarios=False):
    """
    Se obtienen los mejores resultados devueltos por recorrer_BD_secuencial.

    Parameters
    ----------
    cadena_origen : str
        cadena con la dirección objetivo
    r : object
        conexión con la BD Redis con los registros T1
    comentarios : bool
        permite especificar si se desea mostrar comentarios informativos del proceso
    """

    resultados = recorrer_BD_secuencial(cadena_origen, r, comentarios)

    max_completitud = 0
    for resultado in resultados['numero']:
        max_completitud = max(max_completitud, resultado[0].completitud())

    max_confianza = 0
    for resultado in resultados['numero']:
        if resultado[0].completitud() == max_completitud:
            max_confianza = max(max_confianza, resultado[0].confianza())

    mejores_resultados = []
    for resultado in resultados['numero']:
        if resultado[0].completitud() == max_completitud and resultado[0].confianza() == max_confianza:
            mejores_resultados.append(resultado)

    return resultados, mejores_resultados


# import redis
# r = redis.StrictRedis(host='localhost', port=6379, db=11)
# resultados, mejores_resultados = mejores_resultados_recorrer_BD_secuencial('España, La Rioja, Logroño, Calle Eibar, 16', r, comentarios=False)
# print(mejores_resultados)