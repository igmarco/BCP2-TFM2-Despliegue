import re

from DamerauLevenshtein.DL import damerau_levenshtein_similarity, comparacion_palabras

def obtener_direcciones_iniciales_nuevas(regiones,
                                         direcciones_iniciales,
                                         resultados_candidato,
                                         q,
                                         chivato):
    """
    Las regiones iniciales se comparan una por una con la cadena de origen tokenizada, y se almacenan en la cola q
    los mejores resultados obtenidos por cada una de ellas.

    Parameters
    ----------
    regiones : list
        lista de regiones a comparar
    texto_tokenizado : list
        cadena origen tokenizada
    resultados_candidato : list
        array de Numpy que permite calcular la matriz D del algoritmo D-L
    q : object
        cola de deposición de los mejores resultados
    chivato : object
        cola donde se especifica que el proceso ha concluido
    """

    for region in regiones:
        for direccion in direcciones_iniciales:

            nombres = region.nombres()

            mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}
            for candidato in nombres:

                longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)
                texto_tokenizado = re.sub(' +', ' ', re.sub(';|,|\.|¿|\?|¡|!', ' ', direccion[1]).strip()).split()

                comparacion_palabras(texto_tokenizado,
                                    candidato,
                                    longitudes=longitudes,
                                    algoritmo=damerau_levenshtein_similarity,
                                    resultados=resultados_candidato)

                for row in range(len(texto_tokenizado) - min(longitudes)):
                    for column in range(len(longitudes)):
                        if row + column + min(longitudes) < len(texto_tokenizado) and resultados_candidato[row, column] > mejor_resultado['Similaridad']:
                            mejor_resultado = {'Variante': candidato,
                                               'Inicio': row,
                                               'Longitud': column + len(candidato.split()) - 1,
                                               'Similaridad': float(resultados_candidato[row, column])}

            q.put((region.nombre, mejor_resultado))

    chivato.put((1))

def obtener_direcciones(regiones,
                        texto_tokenizado,
                        resultados_candidato,
                        q,
                        chivato):
    """
    Las regiones se comparan una por una con la cadena de origen tokenizada, y se almacenan en la cola q los mejores
    resultados obtenidos por cada una de ellas.

    Parameters
    ----------
    regiones : list
        lista de regiones a comparar
    texto_tokenizado : list
        cadena origen tokenizada
    resultados_candidato : list
        array de Numpy que permite calcular la matriz D del algoritmo D-L
    q : object
        cola de deposición de los mejores resultados
    chivato : object
        cola donde se especifica que el proceso ha concluido
    """

    for region in regiones:

        nombres = region.nombres()

        mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}

        for candidato in nombres:

            resultados_totales_candidato = []
            longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)

            for texto_tokenizado in regiones[region]:
                resultados_totales_candidato.append((comparacion_palabras(texto_tokenizado,
                                                                         candidato,
                                                                         longitudes=longitudes,
                                                                         algoritmo=damerau_levenshtein_similarity,
                                                                         resultados=resultados_candidato),
                                                                         len(texto_tokenizado)))

            for resultados in resultados_totales_candidato:
                for row in range(len(resultados[0])):
                    for column in range(len(resultados[0][0])):
                        if row + column + min(longitudes) < resultados[1] and resultados[0][row, column] > mejor_resultado['Similaridad']:
                            mejor_resultado = {'Variante': candidato,
                                               'Inicio': row,
                                               'Longitud': column + len(candidato.split()) - 1,
                                               'Similaridad': float(resultados[0][row, column])}

        q.put((region.nombre, mejor_resultado))

    chivato.put((1))