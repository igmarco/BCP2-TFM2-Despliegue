from Variables.pesos import pesos_delete_def, pesos_insert_def, pesos_subs_def, pesos_transp_def, contextos


def print_matrix(d, s1, s2):
    """
    Muestra por pantalla la representación de la matriz D (del algoritmo D-L) implementada a través de un diccionario

    Parameters
    ----------
    d : str
        matriz representada como un diccionario cuyas claves son tuplas binarias
    s1 : str
        primera cadena en la aplicación del algoritmo D-L
    s2 : str
        segunda cadena en la aplicación del algoritmo D-L
    """

    for i in range(-1,len(s1)):
        for j in range(-1,len(s2)):
            if (i,j) in d:
                #print("(" + str(i) + "," + str(j) + ") " + str(d[(i,j)]))
                print("[(%02d,%02d) %01d]" % (i, j, d[(i,j)]))
            else:
                print("[(%02d,%02d) %s]" % (i, j, "-"))
        print()

def damerau_levenshtein_distance(s1, s2, pesos_delete=pesos_delete_def,
                                 pesos_insert=pesos_insert_def,
                                 pesos_subs=pesos_subs_def,
                                 pesos_transp=pesos_transp_def,
                                 contextos=contextos,
                                 tasa_contexto=3,  # Empírico
                                 ):
    """
    Devuelve la distancia D-L propia entre dos cadenas con unos parámetros indicados

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

    for i in range(-1, len(s1)):
        d[(i, -1)] = i + 1
    for j in range(-1, len(s2)):
        d[(-1, j)] = j + 1

    for i in range(len(s1)):
        for j in range(len(s2)):

            d[(i, j)] = min(
                d[(i - 1, j)] + pesos_delete[s1[i]],  # deletion
                d[(i, j - 1)] + pesos_insert[s2[j]],  # insertion
            )

            if s1[i] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 1, j - 1)])

            else:
                for i_subs in range(i + 1):
                    for j_subs in range(j + 1):

                        if '#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1] in pesos_subs:

                            if '#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1] in contextos:
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

                                    d[(i, j)] = min(d[(i, j)],
                                                    d[(i_subs - 1, j_subs - 1)] +
                                                    pesos_subs['#_' + s1[i_subs:i + 1] + '#_' + s2[j_subs:j + 1]] *
                                                    peso_total_contexto)

                            d[(i, j)] = min(d[(i, j)],
                                            d[(i_subs - 1, j_subs - 1)] +
                                            pesos_subs['#_' + s1[i_subs:i + 1] + '#_' +  s2[j_subs:j + 1]])

            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + pesos_transp['#_' + s1[i] + '#_' +  s1[i - 1]])  # transposition

    # print_matrix(d, s1, s2)
    return d[len(s1) - 1, len(s2) - 1]


def damerau_levenshtein_similarity(s1, s2, pesos_delete=pesos_delete_def,
                                   pesos_insert=pesos_insert_def,
                                   pesos_subs=pesos_subs_def,
                                   pesos_transp=pesos_transp_def,
                                   contextos=contextos,
                                   tasa_contexto=3,  # Empírico
                                   base_length=None
                                   ):
    """
    Devuelve la similaridad D-L propia entre dos cadenas con unos parámetros indicados.

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

        return 1 - damerau_levenshtein_distance(s1, s2, pesos_delete, pesos_insert, pesos_subs, pesos_transp, contextos,
                                                tasa_contexto) / base_length

def comparacion_palabras(texto_tokenizado, expresion, longitudes, algoritmo, resultados):
    """
    Devuelve la similaridad D-L propia entre dos cadenas con unos parámetros indicados teniendo en cuenta la tolerancia
    ante subcadenas del texto objetivo.

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

    for pos in range(len(texto_tokenizado)):
        for l_ind, l in enumerate(longitudes):
            if pos + min(longitudes) < len(texto_tokenizado):
                if pos + l < len(texto_tokenizado):
                    subtexto = ""
                    for num_tokens in range(l + 1):
                        subtexto += texto_tokenizado[pos + num_tokens] + " "
                    subtexto = subtexto[:-1] if subtexto != '' else ''

                    resultados[pos, l_ind] = algoritmo(subtexto, expresion)

                else:
                    resultados[pos, l_ind] = 0

    return resultados