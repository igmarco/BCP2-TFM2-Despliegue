import numpy as np
import re
import multiprocessing as mp

from ModeloDeDominio.Direccion import Direccion
from ModeloDeDominio.Region import Region, RegionVacia

from Variables.estructura import superestructura, subestructura, pasos_opcionales, pasos_iniciales, origen

from Recorrido.obtener_direcciones_paralelo import obtener_direcciones_iniciales_nuevas, obtener_direcciones

from utiles import recortar_cadena

def recorrer_BD_process(cadena_origen, r, comentarios=True):
    """
    Se recorre la BD contrastando los registros con la cadena objetivo, devolviendo las direcciones coincidentes.
    El proceso se ejecuta de forma paralela.

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

    tolerancia = 0.8

    if __name__ == "__main__":

        direcciones_iniciales = {(Direccion(), cadena_origen), }

        num_processes = mp.cpu_count()
        q = mp.Queue()
        chivato = mp.Queue()

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

            processes = []  # =============================================================== 1

            for process in range(num_processes):
                regions_subarr = []
                for ind_k, k in enumerate(list(regiones)):
                    if ind_k % num_processes == process and k.nombre not in nombres_evaluados[estructura_inicial]:
                        regions_subarr.append(k)

                processes.append(mp.Process(target=obtener_direcciones_iniciales_nuevas,
                                            args=(regions_subarr,
                                                  texto_tokenizado,
                                                  np.zeros((len(texto_tokenizado),3)),
                                                  q,
                                                  chivato)))

                processes[-1].start()

            # print(processes)

            pasos_restantes = num_processes
            while pasos_restantes > 0:
                pasos_restantes -= chivato.get()

            for process in range(num_processes):
                processes[process].join(1)

            while not q.empty():
                nombre_evaluado = q.get()
                # print(nombre_evaluado)
                resultado_dict = nombre_evaluado[1]
                nombres_evaluados[estructura_inicial][nombre_evaluado[0]] = resultado_dict

            for region in regiones:
                if nombres_evaluados[estructura_inicial][region.nombre]['Similaridad'] >= tolerancia:
                    for direccion in direcciones_iniciales:
                        direcc = direccion[0].__copy__()
                        direcc.__dict__[estructura_inicial] = region
                        direcc.__dict__[estructura_inicial].confianza = \
                        nombres_evaluados[estructura_inicial][region.nombre]['Similaridad']

                        nueva_cadena, cadena_restante = recortar_cadena(direccion[1],
                                                       nombres_evaluados[estructura_inicial][region.nombre]['Inicio'],
                                                       nombres_evaluados[estructura_inicial][region.nombre]['Longitud'])

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

            processes = []  # =============================================================== 2

            for process in range(num_processes):
                regions_subdict = {}
                for ind_k, k in enumerate(list(regiones)):
                    if ind_k % num_processes == process and k.nombre not in nombres_evaluados[estructura_actual]:
                        regions_subdict[k] = []
                        for direccion in regiones[k]:
                            regions_subdict[k].append(
                                re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split())

                processes.append(mp.Process(target=obtener_direcciones, args=(regions_subdict,
                                                                              texto_tokenizado,
                                                                              np.zeros((len(texto_tokenizado), 3)),
                                                                              q,
                                                                              chivato)))

                processes[-1].start()

            # print(processes)

            pasos_restantes = num_processes
            while pasos_restantes > 0:
                pasos_restantes -= chivato.get()

            for process in range(num_processes):
                processes[process].join(1)

            while not q.empty():
                nombre_evaluado = q.get()
                # print(nombre_evaluado)
                resultado_dict = nombre_evaluado[1]
                nombres_evaluados[estructura_actual][nombre_evaluado[0]] = resultado_dict

            for region in regiones:
                if nombres_evaluados[estructura_actual][region.nombre]['Similaridad'] >= tolerancia:
                    for direccion in regiones[region]:
                        direcc = direccion[0].__copy__()
                        direcc.__dict__[estructura_actual] = region
                        direcc.__dict__[estructura_actual].confianza = nombres_evaluados[estructura_actual][region.nombre][
                            'Similaridad']

                        cadena_recortada, cadena_restante = recortar_cadena(direccion[1],
                                                           nombres_evaluados[estructura_actual][region.nombre]['Inicio'],
                                                           nombres_evaluados[estructura_actual][region.nombre]['Longitud'])

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

                        processes = []  # =============================================================== 3

                        for process in range(num_processes):
                            regions_subdict = {}
                            for ind_k, k in enumerate(list(regiones)):
                                # En este caso queremos que se evalúen con la parte de cadena anterior
                                if ind_k % num_processes == process:  # and k.nombre not in nombres_evaluados[estructura_actual]:
                                    regions_subdict[k] = []
                                    for direccion in regiones[k]:
                                        regions_subdict[k].append(
                                            re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split())

                            processes.append(mp.Process(target=obtener_direcciones,
                                                        args=(regions_subdict,
                                                              texto_tokenizado,
                                                              np.zeros((len(texto_tokenizado), 3)),
                                                              q,
                                                              chivato)))
                            processes[-1].start()

                        # print(processes)

                        pasos_restantes = num_processes
                        while pasos_restantes > 0:
                            pasos_restantes -= chivato.get()

                        for process in range(num_processes):
                            processes[process].join(1)

                        while not q.empty():
                            nombre_evaluado = q.get()
                            # print(nombre_evaluado)
                            resultado_dict = nombre_evaluado[1]
                            nombres_evaluados[estructura_actual][nombre_evaluado[0]] = resultado_dict

                        for region in regiones:
                            if nombres_evaluados[estructura_actual][region.nombre]['Similaridad'] >= tolerancia:
                                for direccion in regiones[region]:
                                    direcc = direccion[0].__copy__()
                                    direcc.__dict__[estructura_actual] = region
                                    direcc.__dict__[estructura_actual].confianza = \
                                    nombres_evaluados[estructura_actual][region.nombre]['Similaridad']

                                    cadena_recortada, cadena_restante = recortar_cadena(direccion[1],
                                                                       nombres_evaluados[estructura_actual][region.nombre][
                                                                           'Inicio'],
                                                                       nombres_evaluados[estructura_actual][region.nombre][
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

def mejores_resultados_recorrer_BD_process(cadena_origen, r, comentarios=False):
    """
    Se obtienen los mejores resultados devueltos por recorrer_BD_process.

    Parameters
    ----------
    cadena_origen : str
        cadena con la dirección objetivo
    r : object
        conexión con la BD Redis con los registros T1
    comentarios : bool
        permite especificar si se desea mostrar comentarios informativos del proceso
    """

    resultados = recorrer_BD_process(cadena_origen, r, comentarios)

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