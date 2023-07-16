import numpy as np

from ModeloDeDominio.Region import Region, RegionVacia
from Variables.estructura import superestructura, subestructura, dependencia, pasos_opcionales, pasos_iniciales, origen

class Direccion:
    def __init__(self,
                 estado=None,
                 estado_conf=None,
                 ca=None,
                 ca_conf=None,
                 provincia=None,
                 provincia_conf=None,
                 comarca=None,
                 comarca_conf=None,
                 municipio=None,
                 municipio_conf=None,
                 nivel=None,
                 nivel_conf=None,
                 tipovia=None,
                 tipovia_conf=None,
                 via=None,
                 via_conf=None,
                 numero=None,
                 numero_conf=None,
                 codPostal=None,
                 codPostal_conf=None,
                 nombrepropio=None,
                 nombrepropio_conf=None):

        if type(estado) == Region or type(estado) == RegionVacia:
            if estado_conf is not None:
                estado.confianza = estado_conf
            self.estado = estado
        else:
            self.estado = Region('estado', estado, estado_conf) if estado is not None else RegionVacia('estado')

        if type(ca) == Region or type(ca) == RegionVacia:
            if ca_conf is not None:
                ca.confianza = ca_conf
            self.ca = ca
        else:
            self.ca = Region('ca', ca, ca_conf) if ca is not None else RegionVacia('ca')

        if type(provincia) == Region or type(provincia) == RegionVacia:
            if provincia_conf is not None:
                provincia.confianza = provincia_conf
            self.provincia = provincia
        else:
            self.provincia = Region('provincia', provincia, provincia_conf) if provincia is not None else RegionVacia(
                'provincia')

        if type(comarca) == Region or type(comarca) == RegionVacia:
            if comarca_conf is not None:
                comarca.confianza = comarca_conf
            self.comarca = comarca
        else:
            self.comarca = Region('comarca', comarca, comarca_conf) if comarca is not None else RegionVacia('comarca')

        if type(municipio) == Region or type(municipio) == RegionVacia:
            if municipio_conf is not None:
                municipio.confianza = municipio_conf
            self.municipio = municipio
        else:
            self.municipio = Region('municipio', municipio, municipio_conf) if municipio is not None else RegionVacia(
                'municipio')

        if type(nivel) == Region or type(nivel) == RegionVacia:
            if nivel_conf is not None:
                nivel.confianza = nivel_conf
            self.nivel = nivel
        else:
            self.nivel = Region('nivel', nivel, nivel_conf) if nivel is not None else RegionVacia('nivel')

        if type(tipovia) == Region or type(tipovia) == RegionVacia:
            if tipovia_conf is not None:
                tipovia.confianza = tipovia_conf
            self.tipovia = tipovia
        else:
            self.tipovia = Region('tipovia', tipovia, tipovia_conf) if tipovia is not None else RegionVacia('tipovia')

        if type(via) == Region or type(via) == RegionVacia:
            if via_conf is not None:
                via.confianza = via_conf
            self.via = via
        else:
            self.via = Region('via', via, via_conf) if via is not None else RegionVacia('via')

        if type(numero) == Region or type(numero) == RegionVacia:
            if numero_conf is not None:
                numero.confianza = numero_conf
            self.numero = numero
        else:
            self.numero = Region('numero', str(numero), numero_conf) if numero is not None else RegionVacia('numero')

        if type(codPostal) == Region or type(codPostal) == RegionVacia:
            if codPostal_conf is not None:
                codPostal.confianza = codPostal_conf
            self.codPostal = codPostal
        else:
            self.codPostal = Region('codPostal', str(codPostal),
                                    codPostal_conf) if codPostal is not None else RegionVacia('codPostal')

        if type(nombrepropio) == Region or type(nombrepropio) == RegionVacia:
            if nombrepropio_conf is not None:
                nombrepropio.confianza = nombrepropio_conf
            self.nombrepropio = nombrepropio
        else:
            self.nombrepropio = Region('nombrepropio', nombrepropio,
                                       nombrepropio_conf) if nombrepropio is not None else RegionVacia('nombrepropio')

    def comprobar(self, r):
        if type(self.estado) != RegionVacia and self.estado not in Region.regiones('estado', r):
            print('Fallo en el estado')
            return False
        else:
            posibles_cas = self.estado.subregiones('ca', r)
        # print(posibles_cas)

        if type(self.ca) != RegionVacia and self.ca not in posibles_cas:
            print('Fallo en la comunidad autónoma')
            return False
        elif type(self.ca) != RegionVacia:
            posibles_provincias = self.ca.subregiones('provincia', r)
        else:
            posibles_provincias = []
            for ca in posibles_cas:
                posibles_provincias.extend(ca.subregiones('provincia', r))
        # print(posibles_provincias)

        if type(self.provincia) != RegionVacia and self.provincia not in posibles_provincias:
            print('Fallo en la provincia')
            return False
        elif type(self.provincia) != RegionVacia:
            posibles_comarcas = self.provincia.subregiones('comarca', r)
            posibles_municipios = self.provincia.subregiones('municipio', r)
        else:
            posibles_comarcas = []
            posibles_municipios = []
            for provincia in posibles_provincias:
                posibles_comarcas.extend(provincia.subregiones('comarca', r))
                posibles_municipios.extend(provincia.subregiones('municipio', r))
        # print(posibles_comarcas)
        # print(posibles_municipios)

        if type(self.comarca) != RegionVacia and self.comarca not in posibles_comarcas:
            print('Fallo en la comarca')
            return False
        elif type(self.comarca) != RegionVacia:
            posibles_municipios = self.comarca.subregiones('municipio', r)
        # print(posibles_municipios)

        if type(self.municipio) != RegionVacia and self.municipio not in posibles_municipios:
            print('Fallo en el municipio')
            return False
        elif type(self.municipio) != RegionVacia:
            posibles_niveles = self.municipio.subregiones('nivel', r)
            posibles_vias = self.municipio.subregiones('via', r)
        else:
            posibles_niveles = []
            posibles_vias = []
            for municipio in posibles_municipios:
                posibles_niveles.extend(municipio.subregiones('nivel', r))
                posibles_vias.extend(municipio.subregiones('via', r))
        # print(posibles_niveles)
        # print(posibles_vias)

        if type(self.nivel) != RegionVacia and self.nivel not in posibles_niveles:
            print('Fallo en el nivel')
            return False
        elif type(self.nivel) != RegionVacia:
            posibles_vias = self.nivel.subregiones('via', r)
        # print(posibles_vias)

        if type(self.tipovia) != RegionVacia and self.tipovia not in Region.regiones('tipovia', r):
            print('Fallo en el tipo de vía')
            return False
        elif type(self.tipovia) != RegionVacia:
            posibles_vias_filtradas = []
            for via in posibles_vias:
                i = 0
                añadido = False
                elementos = via.elementos(r)
                while i < len(elementos) and not añadido:
                    if elementos[i]['nombreTipoVia'] == self.tipovia.nombre:
                        posibles_vias_filtradas.append(via)
                        añadido = True
                    i += 1
            posibles_vias = posibles_vias_filtradas
        # print(posibles_vias)

        if type(self.via) != RegionVacia and self.via not in posibles_vias:
            print('Fallo en la vía')
            return False
        elif type(self.via) != RegionVacia:
            posibles_numeros = self.via.subregiones('numero', r)
            posibles_codPostales = self.via.subregiones('codPostal', r)
        else:
            posibles_numeros = []
            posibles_codPostales = []
            for via in posibles_vias:
                posibles_numeros.extend(via.subregiones('numero', r))
                posibles_codPostales.extend(via.subregiones('codPostal', r))
        # print(posibles_numeros)
        # print(posibles_codPostales)

        if type(self.codPostal) != RegionVacia and self.codPostal not in posibles_codPostales:
            print('Fallo en el código postal')
            return False

        if type(self.numero) != RegionVacia and self.numero not in posibles_numeros:
            print('Fallo en el número')
            return False

        if type(self.codPostal) != RegionVacia and type(self.numero) != RegionVacia:
            numero_en_codPostal = False
            for elemento in self.numero.elementos(r):
                if elemento['codPostal'] == self.codPostal:
                    numero_en_codPostal = True
                    break;
            if not numero_en_codPostal:
                print('Fallo en la correspondencia número - código postal')
                return False

        if type(self.nombrepropio) != RegionVacia:
            nombrepropio_en_numero = False
            nombrepropio_en_codPostal = False
            for elemento in self.nombrepropio.elementos(r):
                reg_numero = Region('numero', str(elemento['numero']))
                reg_codPostal = Region('codPostal', str(elemento['codPostal']))
                if type(self.numero) != RegionVacia and reg_numero == self.numero:
                    nombrepropio_en_numero = True
                elif type(self.numero) == RegionVacia and reg_numero in posibles_numeros:
                    nombrepropio_en_numero = True

                if type(self.codPostal) != RegionVacia and reg_codPostal == self.codPostal:
                    nombrepropio_en_codPostal = True
                elif type(self.codPostal) == RegionVacia and reg_codPostal in posibles_codPostales:
                    nombrepropio_en_codPostal = True
            if not nombrepropio_en_codPostal or not nombrepropio_en_numero:
                print('Fallo en el nombre propio')
                return False

        return True

    def confianza(self, pesos=None):
        if pesos is None:
            pesos = np.array([0.5, 0.75, 0.75, 0.25, 1, 0.5, 1, 1.5, 0.5, 0.5, 1.5])
        else:
            pesos = np.array(pesos)

        reales = np.zeros((11))

        resultado = 0
        if type(self.estado) != RegionVacia:
            resultado += self.estado.confianza * pesos[0] if self.estado.confianza is not None else pesos[0]
            reales[0] = 1
        if type(self.ca) != RegionVacia:
            resultado += self.ca.confianza * pesos[1] if self.ca.confianza is not None else pesos[1]
            reales[1] = 1
        if type(self.provincia) != RegionVacia:
            resultado += self.provincia.confianza * pesos[2] if self.ca.confianza is not None else pesos[2]
            reales[2] = 1
        if type(self.comarca) != RegionVacia:
            resultado += self.comarca.confianza * pesos[3] if self.ca.confianza is not None else pesos[3]
            reales[3] = 1
        if type(self.municipio) != RegionVacia:
            resultado += self.municipio.confianza * pesos[4] if self.ca.confianza is not None else pesos[4]
            reales[4] = 1
        if type(self.nivel) != RegionVacia:
            resultado += self.nivel.confianza * pesos[5] if self.ca.confianza is not None else pesos[5]
            reales[5] = 1
        if type(self.tipovia) != RegionVacia:
            resultado += self.tipovia.confianza * pesos[6] if self.ca.confianza is not None else pesos[6]
            reales[6] = 1
        if type(self.via) != RegionVacia:
            resultado += self.via.confianza * pesos[7] if self.ca.confianza is not None else pesos[7]
            reales[7] = 1
        if type(self.numero) != RegionVacia:
            resultado += self.numero.confianza * pesos[8] if self.ca.confianza is not None else pesos[8]
            reales[8] = 1
        if type(self.codPostal) != RegionVacia:
            resultado += self.codPostal.confianza * pesos[9] if self.ca.confianza is not None else pesos[9]
            reales[9] = 1
        if type(self.nombrepropio) != RegionVacia:
            resultado += self.nombrepropio.confianza * pesos[10] if self.ca.confianza is not None else pesos[10]
            reales[10] = 1

        return resultado / np.sum(reales * pesos)

    def posibles_subregiones(self, estructura, r):
        if type(self.estado) == RegionVacia:
            estados = Region.regiones('estado', r)
        else:
            estados = [self.estado]
        if estructura == 'estado':
            return estados

        if type(self.ca) == RegionVacia:
            cas = []
            for estado in estados:
                cas.extend(estado.subregiones('ca', r))
        else:
            cas = [self.ca]
        if estructura == 'ca':
            return cas

        if type(self.provincia) == RegionVacia:
            provincias = []
            for ca in cas:
                provincias.extend(ca.subregiones('provincia', r))
        else:
            provincias = [self.provincia]
        if estructura == 'provincia':
            return provincias

        if type(self.comarca) == RegionVacia:
            comarcas = []
            for provincia in provincias:
                comarcas.extend(provincia.subregiones('comarca', r))
        else:
            comarcas = [self.comarca]
        if estructura == 'comarca':
            return comarcas

        if type(self.municipio) == RegionVacia:
            municipios = []
            if type(self.comarca) == RegionVacia:
                for provincia in provincias:
                    municipios.extend(provincia.subregiones('municipio', r))
            else:
                municipios = self.comarca.subregiones('municipio', r)
        else:
            municipios = [self.municipio]
        if estructura == 'municipio':
            return municipios

        if type(self.nivel) == RegionVacia:
            niveles = []
            for municipio in municipios:
                niveles.extend(municipio.subregiones('nivel', r))
        else:
            niveles = [self.nivel]
        if estructura == 'nivel':
            return niveles

        if type(self.via) == RegionVacia:
            vias = []
            if type(self.nivel) == RegionVacia:
                for municipio in municipios:
                    vias.extend(municipio.subregiones('via', r))
            else:
                vias = self.nivel.subregiones('via', r)
            if type(self.tipovia) != RegionVacia:
                vias_aux = []
                vias_tipovia = self.tipovia.subregiones('via', r)
                for via in vias:
                    if via in vias_tipovia:
                        vias_aux.append(via)
                vias = vias_aux
        else:
            vias = [self.via]
        if estructura == 'via':
            return vias

        if type(self.codPostal) == RegionVacia:
            codPostales = []
            for via in vias:
                codPostales.extend(via.subregiones('codPostal', r))
            if type(self.nombrepropio) != RegionVacia:
                codPostales_aux = []
                codPostales_nombrepropio = self.nombrepropio.subregiones('codPostal', r)
                for codPostal in codPostales:
                    if codPostal in codPostales_nombrepropio:
                        codPostales_aux.append(codPostal)
                codPostales = codPostales_aux
        else:
            codPostales = [self.codPostal]
        if estructura == 'codPostal':
            return codPostales

        if type(self.numero) == RegionVacia:
            numeros = []
            for via in vias:
                numeros.extend(via.subregiones('numero', r))
            if type(self.nombrepropio) != RegionVacia:
                numeros_aux = []
                numeros_nombrepropio = self.nombrepropio.subregiones('numero', r)
                for numero in numeros:
                    if numero in numeros_nombrepropio:
                        numeros_aux.append(numero)
                numeros = numeros_aux
        else:
            numeros = [self.numero]
        if estructura == 'numero':
            return numeros

        return None

    def posibles_subdirecciones(self, estructura, r):

        direcciones = []

        if type(self.__dict__[estructura]) != RegionVacia:
            direcciones = [self]
        elif estructura == 'estado':
            regiones = Region.regiones('estado', r)
            for region in regiones:
                nueva_direccion = self.__copy__()
                nueva_direccion.__dict__['estado'] = region
                direcciones.append(nueva_direccion)
        else:

            estructura_limite = estructura
            estructura_vacia = None

            seguir = True
            while estructura_limite != 'estado' and seguir:
                paso_obligatorio = None
                paso_opcional = None
                for superestruct in superestructura[estructura_limite]:
                    if superestruct not in pasos_opcionales:
                        paso_obligatorio = superestruct
                    else:
                        paso_opcional = superestruct
                    if type(self.__dict__[superestruct]) != RegionVacia:
                        seguir = False
                estructura_vacia = estructura_limite
                estructura_limite = paso_obligatorio

            if estructura_limite == 'estado' and seguir:
                regiones = Region.regiones('estado', r)
                estructura_vacia = 'estado'
            else:

                if paso_opcional is not None and type(self.__dict__[paso_opcional]) != RegionVacia:
                    estructura_limite = paso_opcional

                regiones = self.__dict__[estructura_limite].subregiones(estructura_vacia, r)

                if estructura_vacia in dependencia:
                    for superior in dependencia[estructura_vacia]:
                        if superior in self.__dict__:
                            regiones_filtro = self.__dict__[superior].subregiones(estructura_vacia, r)

                            # print(len(regiones), len(regiones_filtro), len(set(regiones) & set(regiones_filtro)))
                            regiones = list(set(regiones) & set(regiones_filtro))

            for region in regiones:
                nueva_direccion = self.__copy__()
                nueva_direccion.__dict__[estructura_vacia] = region
                direcciones.extend(nueva_direccion.posibles_subdirecciones(estructura, r))

        return direcciones

    def completitud(self, pesos=None):
        if pesos is None:
            pesos = np.array([1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0])
            pesos = pesos / np.sum(pesos)

        return (
                (type(self.estado) != RegionVacia or self.estado.confianza is None) * pesos[0] +
                (type(self.ca) != RegionVacia or self.ca.confianza is None) * pesos[1] +
                (type(self.provincia) != RegionVacia or self.provincia.confianza is None) * pesos[2] +
                (type(self.comarca) != RegionVacia or self.comarca.confianza is None) * pesos[3] +
                (type(self.municipio) != RegionVacia or self.municipio.confianza is None) * pesos[4] +
                (type(self.nivel) != RegionVacia or self.nivel.confianza is None) * pesos[5] +
                (type(self.tipovia) != RegionVacia or self.tipovia.confianza is None) * pesos[6] +
                (type(self.via) != RegionVacia or self.via.confianza is None) * pesos[7] +
                (type(self.numero) != RegionVacia or self.numero.confianza is None) * pesos[8] +
                (type(self.codPostal) != RegionVacia or self.codPostal.confianza is None) * pesos[9] +
                (type(self.nombrepropio) != RegionVacia or self.nombrepropio.confianza is None) * pesos[10]
        )

    def __repr__(self):
        return (
                self.estado.__str__() + '\n' +
                self.ca.__str__() + '\n' +
                self.provincia.__str__() + '\n' +
                self.comarca.__str__() + '\n' +
                self.municipio.__str__() + '\n' +
                self.nivel.__str__() + '\n' +
                self.tipovia.__str__() + '\n' +
                self.via.__str__() + '\n' +
                self.codPostal.__str__() + '\n' +
                self.numero.__str__() + '\n' +
                self.nombrepropio.__str__() + '\n'
        )

    def __str__(self):
        return self.__repr__()

    def __copy__(self):
        return Direccion(estado=self.estado.__copy__(),
                         ca=self.ca.__copy__(),
                         provincia=self.provincia.__copy__(),
                         comarca=self.comarca.__copy__(),
                         municipio=self.municipio.__copy__(),
                         nivel=self.nivel.__copy__(),
                         tipovia=self.tipovia.__copy__(),
                         via=self.via.__copy__(),
                         numero=self.numero.__copy__(),
                         codPostal=self.codPostal.__copy__(),
                         nombrepropio=self.nombrepropio.__copy__())

    def __eq__(self, direccion):
        elementos = ['estado', 'ca', 'provincia', 'comarca', 'municipio', 'nivel',
                     'tipovia', 'via', 'numero', 'codPostal', 'nombrepropio']

        for elemento in elementos:
            if self.__dict__[elemento] != direccion.__dict__[elemento]:
                return False

        return True

    def __hash__(self):
        elementos = ['estado', 'ca', 'provincia', 'comarca', 'municipio', 'nivel',
                     'tipovia', 'via', 'numero', 'codPostal', 'nombrepropio']

        concatenate = ''
        for elemento in elementos:
            concatenate += self.__dict__[elemento].estructura + self.__dict__[elemento].nombre

        return hash(concatenate)