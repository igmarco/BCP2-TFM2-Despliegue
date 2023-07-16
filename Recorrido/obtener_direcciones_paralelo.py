from DamerauLevenshtein.DL import damerau_levenshtein_similarity, comparacion_palabras

def obtener_direcciones_iniciales_nuevas(regiones,
                                         texto_tokenizado,
                                         resultados_candidato,
                                         q,
                                         chivato):

    for region in regiones:

        nombres = region.nombres()

        mejor_resultado = {'Variante': '', 'Inicio': 0, 'Longitud': 0, 'Similaridad': -1}
        for candidato in nombres:

            longitudes = range(len(candidato.split()) - 1, len(candidato.split()) + 2)

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
                        resultados_candidato,
                        q,
                        chivato):

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