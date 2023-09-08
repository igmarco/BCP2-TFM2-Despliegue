import sys
sys.path.append('../Despliegue del servidor')

from fastapi import FastAPI
import uvicorn

from typing import Union
import redis

from Recorrido.recorrer_BD_secuencial import mejores_resultados_recorrer_BD_secuencial, mejores_resultados_recorrer_BD_completa_secuencial
from Recorrido.recorrer_BD_paralelo import mejores_resultados_recorrer_BD_process

from Entrenamiento.entrenamiento_pesos import entrenar_pesos_fila


app = FastAPI()

@app.get("/")
def description():
    """
    Se devuelve una descripción en castellano e inglés del servicio ofrecido por el API REST.
    """
    return {"Descripción (ESP)": "El servicio DS-AIT (Herramienta de Ciencia de Datos aplicada a la Identificación de Direcciones)es una herramienta que permite identificar la información geográfica concreta a partir de una cadena de texto libre. Este proceso se lleva a cabo a través del contraste con una base de datos normalizada, alimentada con información de IDERioja.",
            "Description (ENG)": "The DS-AIT service (Data Science Tool applied to Address Identification) is a tool that allows the identification of specific geographic information from a free text string. This process is carried out through the contrast with a normalized database, fed with information from IDERioja."}


@app.get("/identification/sequential/{string}")
def identification_secuential(string: str,
              only_best_results: bool = True,
              delete_from_server: bool = True):
    """
    Se realiza el contraste con los registros T1 para obtener las direcciones reales coincidentes con la cadena
    objetivo (versión secuencial).

    Parameters
    ----------
    string : str
        cadena con la dirección objetivo
    only_best_results : bool
        permite especificar si se desea mostrar todos los resultados o solo los mejores
    delete_from_server : bool
        permite especificar si se desea que se almacene la petición en el servidor
    """

    if not delete_from_server:
        with open('DatosCSV/peticiones.txt', 'a', encoding='utf-8') as peticiones:
            peticiones.write(string + '\n')

    r = redis.StrictRedis(host='localhost', port=6379, db=11)
    resultados, mejores_resultados = mejores_resultados_recorrer_BD_secuencial(string, r, comentarios=False)

    if only_best_results:
        return mejores_resultados
    else:
        return resultados


# @app.get("/identification/parallel/{string}")
# def identification_parallel(string: str,
#               only_best_results: bool = True,
#               delete_from_server: bool = True):
#     """
#     Se realiza el contraste con los registros T1 para obtener las direcciones reales coincidentes con la cadena
#     objetivo (versión paralela).
#
#     Parameters
#     ----------
#     string : str
#         cadena con la dirección objetivo
#     only_best_results : bool
#         permite especificar si se desea mostrar todos los resultados o solo los mejores
#     delete_from_server : bool
#         permite especificar si se desea que se almacene la petición en el servidor
#     """
#
#     if not delete_from_server:
#         with open('DatosCSV/peticiones.txt', 'a', encoding='utf-8') as peticiones:
#             peticiones.write(string + '\n')
#
#     r = redis.StrictRedis(host='localhost', port=6379, db=11)
#     resultados, mejores_resultados = mejores_resultados_recorrer_BD_process(string, r, comentarios=False)
#
#     print(mejores_resultados)
#
#     if only_best_results:
#         return mejores_resultados
#     else:
#         return resultados


@app.get("/identification/sequential/complete/{string}")
def identification_complete_sequential(string: str,
              only_best_results: bool = True,
              delete_from_server: bool = True):
    """
    Se realiza el contraste con los registros T1 para obtener las direcciones reales coincidentes con la cadena
    objetivo (versión secuencial). Se emplea el algoritmo de contraste completo con la BD.

    Parameters
    ----------
    string : str
        cadena con la dirección objetivo
    only_best_results : bool
        permite especificar si se desea mostrar todos los resultados o solo los mejores
    delete_from_server : bool
        permite especificar si se desea que se almacene la petición en el servidor
    """

    if not delete_from_server:
        with open('DatosCSV/peticiones.txt', 'a', encoding='utf-8') as peticiones:
            peticiones.write(string + '\n')

    r = redis.StrictRedis(host='localhost', port=6379, db=11)
    resultados, mejores_resultados = mejores_resultados_recorrer_BD_completa_secuencial(string, r, comentarios=False)

    if only_best_results:
        return mejores_resultados
    else:
        return resultados


@app.post("/training/{cadena}")
def training(cadena: str,
             estado: Union[str, None] = None,
             ca: Union[str, None] = None,
             provincia: Union[str, None] = None,
             comarca: Union[str, None] = None,
             municipio: Union[str, None] = None,
             nivel: Union[str, None] = None,
             tipovia: Union[str, None] = None,
             via: Union[str, None] = None,
             numero: Union[str, None] = None,
             codPostal: Union[str, None] = None,
             nombrepropio: Union[str, None] = None, ):
    """
    Se ejecuta un entrenamiento con el registro introducido. Para ello se utiliza como validación tanto la confianza
    del resultado como el contraste con los valores reales introducidos.

    Parameters
    ----------
    cadena : str
        cadena con la dirección objetivo
    estado : str
        Region estado
    ca : str
        Region ca
    provincia : str
        Region provincia
    comarca : str
        Region comarca
    municipio : str
        Region municipio
    nivel : str
        Region nivel
    tipovia : str
        Region tipovia
    via : str
        Region via
    numero : str
        Region numero
    codPostal : str
        Region codPostal
    nombrepropio : str
        Region nombrepropio
    """

    r_BD = redis.StrictRedis(host='localhost', port=6379, db=11)
    r_pesos = redis.StrictRedis(host='localhost', port=6379, db=12)

    fila_dict = {'cadena': cadena,
                 'estado': estado,
                 'ca': ca,
                 'provincia': provincia,
                 'comarca': comarca,
                 'municipio': municipio,
                 'nivel': nivel,
                 'tipovia': tipovia,
                 'via': via,
                 'numero': numero,
                 'codPostal': codPostal,
                 'nombrepropio': nombrepropio,
                }

    entrenar_pesos_fila(fila_dict, r_BD, r_pesos)

    return 'Done! Thanks!'

if __name__ == "__main__":
    # http://127.0.0.1:8000/
    # http://127.0.0.1:8000/docs
    # http://127.0.0.1:8000/identification/sequential/España
    # http://127.0.0.1:8000/identification/parallel/España

    uvicorn.run(app, host="0.0.0.0", port=8000)
