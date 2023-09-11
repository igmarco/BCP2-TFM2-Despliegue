# BCP2 (TFM2) - Despliegue
Parte del Trabajo de Fin de Máster del Máster en Ciencia de Datos y Aprendizaje Automático de la Universidad de La Rioja. Despliegue de la API REST con el servicio de georreferenciación.

## Estructura del proyecto:
### _DamerauLevenshtein_

Funciones de comparación de cadenas de texto a través de la distancia Damerau-Levenshtein modificada. Modificación para el entrenamiento de los pesos del algoritmo.

### _DatosCSV_

Ficheros de recogida de datos a través de la API REST.

### _Entrenamiento_

Funciones de entrenamiento de los pesos del algoritmo a través de direcciones concretas.

### _ModeloDeDominio_

Implementación de las clases _Direccion_, _Region_ y _RegionVacia_ para la implementación del algoritmo de recorrido de la BD.

### _Recorrido_

Funciones de recorrido de la BD para la comparación de direcciones libres con los registros de referencia de la BD en Redis.

### _Variables_

Variables de configuración de los algoritmos. Relaciones entre estructuras geográficas y pesos para el algoritmo Damerau-Levenshtein modificado.


Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
