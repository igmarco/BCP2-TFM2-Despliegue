from DamerauLevenshtein.DL import damerau_levenshtein_distance, print_matrix

from Variables.pesos import pesos_delete_def, pesos_insert_def, pesos_subs_def, pesos_transp_def, contextos

def actualizar_temporales(proceso, s1, s2):
    """
    Devuelve en base al proceso seguido por el algoritmo D-L las matrices de correspondencias, contextos y usos.

    Parameters
    ----------
    proceso : list
        lista de pasos que ha seguido el algoritmo D-L para alcanzar el resultado final
    s2 : str
        primera cadena en la aplicación del algoritmo D-L
    s1 : str
        segunda cadena en la aplicación del algoritmo D-L
    """

    pesos_delete_correspondencias_tmp = {}
    pesos_insert_correspondencias_tmp = {}
    pesos_subs_correspondencias_tmp = {}
    pesos_transp_correspondencias_tmp = {}
    contextos_registrados_tmp = {}
    uso_letras_tmp = {}

    for paso in proceso:
        if paso[0] == 'delete':
            if paso[1] in pesos_delete_correspondencias_tmp:
                pesos_delete_correspondencias_tmp[paso[1]] += 1
            else:
                pesos_delete_correspondencias_tmp[paso[1]] = 1
        elif paso[0] == 'insert':
            if paso[1] in pesos_insert_correspondencias_tmp:
                pesos_insert_correspondencias_tmp[paso[1]] += 1
            else:
                pesos_insert_correspondencias_tmp[paso[1]] = 1
        elif paso[0] == 'subs':
            if '#_' + paso[1] + '#_' + paso[2] in pesos_insert_correspondencias_tmp:
                pesos_subs_correspondencias_tmp['#_' + paso[1] + '#_' + paso[2]] += 1
            else:
                pesos_subs_correspondencias_tmp['#_' + paso[1] + '#_' + paso[2]] = 1
            if (paso[1], paso[2]) in contextos_registrados_tmp:
                contextos_registrados_tmp['#_' + paso[1] + '#_' + paso[2]].extend(paso[3])
            else:
                contextos_registrados_tmp['#_' + paso[1] + '#_' + paso[2]] = paso[3]
        elif paso[0] == 'transp':
            if '#_' + paso[1] + '#_' + paso[2] in pesos_insert_correspondencias_tmp:
                pesos_transp_correspondencias_tmp['#_' + paso[1] + '#_' + paso[2]] += 1
            else:
                pesos_transp_correspondencias_tmp['#_' + paso[1] + '#_' + paso[2]] = 1

    for s in [s1, s2]:
        for char in s:
            if char in uso_letras_tmp:
                uso_letras_tmp[char] += 1
            else:
                uso_letras_tmp[char] = 1

    return pesos_delete_correspondencias_tmp, \
           pesos_insert_correspondencias_tmp, \
           pesos_subs_correspondencias_tmp, \
           pesos_transp_correspondencias_tmp, \
           contextos_registrados_tmp, \
           uso_letras_tmp


def damerau_levenshtein_distance_training(s1, s2, pesos_delete=pesos_delete_def,
                                         pesos_insert=pesos_insert_def,
                                         pesos_subs=pesos_subs_def,
                                         pesos_transp=pesos_transp_def,
                                         contextos=contextos,
                                         tasa_contexto=3,  # Empírico
                                         ):
    """
    Modificación del algoritmo D-L propio para el entrenamiento de pesos. Devuelve, además del resultado, los
    diccionarios de correspondencias.

    Parameters
    ----------
    s1 : str
        primera cadena en la aplicación del algoritmo D-L
    s2 : str
        segunda cadena en la aplicación del algoritmo D-L
    pesos_delete : dict
        diccionario con pesos para las eliminaciones
    pesos_insert : dict
        diccionario con pesos para las inserciones
    pesos_subs : dict
        diccionario con pesos para las sustituciones
    pesos_transp : dict
        diccionario con pesos para las transposiciones
    contextos : dict
        diccionario con contextos y sus pesos para las sustituciones
    tasa_contexto : int
        grado del factor de impacto de la coincidencia de un contexto
    """

    d = {}

    d[(-1, -1)] = (0, [])

    for i in range(0, len(s1)):
        d[(i, -1)] = (i + 1, d[(i-1,-1)][1] + [('delete', s1[i])])
    for j in range(0, len(s2)):
        d[(-1, j)] = (j + 1, d[(-1,j-1)][1] + [('insert', s2[j])])

    for i in range(len(s1)):
        for j in range(len(s2)):

            if d[(i - 1, j)][0] + pesos_delete[s1[i]] < d[(i, j - 1)][0] + pesos_insert[s2[j]]:
                # deletion
                d[(i, j)] = (d[(i - 1, j)][0] + pesos_delete[s1[i]], d[(i - 1, j)][1].copy())
                d[(i, j)][1].append(('delete', s1[i]))
            else:
                # insertion
                d[(i, j)] = (d[(i, j - 1)][0] + pesos_insert[s2[j]], d[(i, j - 1)][1].copy())
                d[(i, j)][1].append(('insert', s2[j]))

            if s1[i] == s2[j] and d[(i - 1, j - 1)][0] < d[(i, j)][0]:
                d[(i, j)] = (d[(i - 1, j - 1)][0], d[(i - 1, j - 1)][1].copy())

            else:
                for i_subs in range(i + 1):
                    for j_subs in range(j + 1):

                        if '#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1] in pesos_subs:

                            if '#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1] in contextos:
                                # substitution (context)
                                for contexto in contextos['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]]:
                                    peso_total_contexto = 1 - contexto[1] * max(
                                        1 - damerau_levenshtein_distance(s1[:i_subs], contexto[0], pesos_delete,
                                                                         pesos_insert, pesos_subs, pesos_transp,
                                                                         contextos, tasa_contexto) / max(
                                            len(s1[i_subs:i + 1]), len(s2[j_subs:j + 1])),
                                        1 - damerau_levenshtein_distance(s1[i + 1:], contexto[0], pesos_delete,
                                                                         pesos_insert, pesos_subs, pesos_transp,
                                                                         contextos, tasa_contexto) / max(
                                            len(s1[i_subs:i + 1]), len(s2[j_subs:j + 1]))) ** tasa_contexto

                                    if (d[(i_subs - 1, j_subs - 1)][0] +
                                            pesos_subs['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]] *
                                            peso_total_contexto < d[(i, j)][0]):
                                        d[(i, j)] = (d[(i_subs - 1, j_subs - 1)] +
                                                        pesos_subs['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]] *
                                                        peso_total_contexto, d[(i_subs - 1, j_subs - 1)][1].copy())
                                        d[(i, j)][1].append(('subs',
                                                             s1[i_subs:i + 1],
                                                             s2[j_subs:j + 1],
                                                             [contexto[0]]))

                            if (d[(i_subs - 1, j_subs - 1)][0] +
                                            pesos_subs['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]] < d[(i, j)][0]):
                                # substitution (no context)
                                d[(i, j)] = (d[(i_subs - 1, j_subs - 1)][0] +
                                                pesos_subs['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]], d[(i_subs - 1, j_subs - 1)][1].copy())
                                d[(i, j)][1].append(('subs', s1[i_subs:i + 1], s2[j_subs:j + 1], [s1[:i_subs], s1[i + 1:]]))

            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j] and d[i - 2, j - 2][0] + pesos_transp['#_' + s1[i] + '#_' + s1[i - 1]] < d[(i, j)][0]:
                # transposition
                d[(i, j)] = (d[i - 2, j - 2][0] + pesos_transp['#_' + s1[i] + '#_' + s1[i - 1]], d[i - 2, j - 2][1].copy())
                d[(i, j)][1].append(('transp', s1[i], s1[i - 1]))

    # print_matrix(d, s1, s2)

    pesos_delete_correspondencias_tmp, \
    pesos_insert_correspondencias_tmp, \
    pesos_subs_correspondencias_tmp, \
    pesos_transp_correspondencias_tmp, \
    contextos_registrados_tmp, \
    uso_letras_tmp = actualizar_temporales(d[len(s1) - 1, len(s2) - 1][1], s1, s2)

    return d[len(s1) - 1, len(s2) - 1][0], \
           pesos_delete_correspondencias_tmp, \
           pesos_insert_correspondencias_tmp, \
           pesos_subs_correspondencias_tmp, \
           pesos_transp_correspondencias_tmp, \
           contextos_registrados_tmp, \
           uso_letras_tmp


def damerau_levenshtein_similarity_training(s1, s2, pesos_delete=pesos_delete_def,
                                   pesos_insert=pesos_insert_def,
                                   pesos_subs=pesos_subs_def,
                                   pesos_transp=pesos_transp_def,
                                   contextos=contextos,
                                   tasa_contexto=3,  # Empírico
                                   base_length=None
                                   ):
    """
    Modificación del algoritmo D-L propio (similaridad) para el entrenamiento de pesos. Devuelve, además del resultado,
    los diccionarios de correspondencias.

    Parameters
    ----------
    s1 : str
        primera cadena en la aplicación del algoritmo D-L
    s2 : str
        segunda cadena en la aplicación del algoritmo D-L
    pesos_delete : dict
        diccionario con pesos para las eliminaciones
    pesos_insert : dict
        diccionario con pesos para las inserciones
    pesos_subs : dict
        diccionario con pesos para las sustituciones
    pesos_transp : dict
        diccionario con pesos para las transposiciones
    contextos : dict
        diccionario con contextos y sus pesos para las sustituciones
    tasa_contexto : int
        grado del factor de impacto de la coincidencia de un contexto
    base_length : int
        factor de longitud aplicable; si es None, se toma la longitud máxima entre las cadenas s1 y s2
    """

    if base_length == None:
        base_length = max(len(s1), len(s2))
        # base_length = len(s2)

        resultado, \
        pesos_delete_correspondencias_tmp, \
        pesos_insert_correspondencias_tmp, \
        pesos_subs_correspondencias_tmp, \
        pesos_transp_correspondencias_tmp, \
        contextos_registrados_tmp, \
        uso_letras_tmp = damerau_levenshtein_distance_training(s1, s2, pesos_delete, pesos_insert, pesos_subs, pesos_transp, contextos,
                                              tasa_contexto)

        return 1 - resultado / base_length, \
           pesos_delete_correspondencias_tmp, \
           pesos_insert_correspondencias_tmp, \
           pesos_subs_correspondencias_tmp, \
           pesos_transp_correspondencias_tmp, \
           contextos_registrados_tmp, \
           uso_letras_tmp


def comparacion_palabras_training(texto_tokenizado, expresion, longitudes, resultados):
    """
    Devuelve la similaridad D-L propia entre dos cadenas con unos parámetros indicados teniendo en cuenta la tolerancia
    ante subcadenas del texto objetivo. Devuelve, además del resultado, los diccionarios de correspondencias.

    Parameters
    ----------
    texto_tokenizado : list
        primera cadena (objetivo) en la aplicación del algoritmo D-L, separada por tokens
    expresion : str
        segunda cadena en la aplicación del algoritmo D-L
    longitudes : list
        vector de enteros con las cantidades de tokens a considerar de la cadena objetivo
    algoritmo : object
        algoritmo de comparación de cadenas a aplicar
    resultados : dict
        vector base con los resultados de la ejecución
    """

    max_resultado = -1
    pesos_delete_correspondencias_tmp_max = None
    pesos_insert_correspondencias_tmp_max = None
    pesos_subs_correspondencias_tmp_max = None
    pesos_transp_correspondencias_tmp_max = None
    contextos_registrados_tmp_max = None
    uso_letras_tmp_max = None

    for pos in range(len(texto_tokenizado)):
        for l_ind, l in enumerate(longitudes):
            if pos + min(longitudes) < len(texto_tokenizado):
                if pos + l < len(texto_tokenizado):
                    subtexto = ""
                    for num_tokens in range(l + 1):
                        subtexto += texto_tokenizado[pos + num_tokens] + " "
                    subtexto = subtexto[:-1] if subtexto != '' else ''

                    resultados[pos, l_ind], \
                    pesos_delete_correspondencias_tmp, \
                    pesos_insert_correspondencias_tmp, \
                    pesos_subs_correspondencias_tmp, \
                    pesos_transp_correspondencias_tmp, \
                    contextos_registrados_tmp, \
                    uso_letras_tmp = damerau_levenshtein_similarity_training(subtexto, expresion)

                    if resultados[pos, l_ind] > max_resultado:
                        max_resultado = resultados[pos, l_ind]
                        pesos_delete_correspondencias_tmp_max = pesos_delete_correspondencias_tmp
                        pesos_insert_correspondencias_tmp_max = pesos_insert_correspondencias_tmp
                        pesos_subs_correspondencias_tmp_max = pesos_subs_correspondencias_tmp
                        pesos_transp_correspondencias_tmp_max = pesos_transp_correspondencias_tmp
                        contextos_registrados_tmp_max = contextos_registrados_tmp
                        uso_letras_tmp_max = uso_letras_tmp

                else:
                    resultados[pos, l_ind] = 0


    return pesos_delete_correspondencias_tmp_max, \
           pesos_insert_correspondencias_tmp_max, \
           pesos_subs_correspondencias_tmp_max, \
           pesos_transp_correspondencias_tmp_max, \
           contextos_registrados_tmp_max, \
           uso_letras_tmp_max