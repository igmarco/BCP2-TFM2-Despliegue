from utiles import decode_json

class Region:
    """
    Representa el nombre o topónimo de una región determinada (estado,
    comunidad autónoma, provincia, vía, etc.). Por tanto, se puede asociar con 0-*
    regiones reales definidas en la base de datos de referencia.

    Attributes
    ----------
    estructura : str
        tipo de región. Valores posibles: {“estado”, “ca”, “provincia”,
        “comarca”, “municipio”, “nivel”, “tipovia”, “numero”, “codPostal”,
        “nombrepropio”}
    nombre : str
        nombre concreto de la región
    confianza : float
        nivel de confianza para la cadena match
    match : str
        cadena de una dirección con la que se asocia el nombre de región.
    """

    def __init__(self, estructura, nombre, confianza=None, match=None):
        self.estructura = estructura
        self.nombre = nombre
        self.confianza = confianza
        self.match = match

    @staticmethod
    def regiones(estructura, redis_connection):
        """
        Devuelve todas las Regiones (nombres de región) que se
        correspondan con la estructura especificada.

        Parameters
        ----------
        estructura : str
            tipo de región. Valores posibles: {“estado”, “ca”, “provincia”,
            “comarca”, “municipio”, “nivel”, “tipovia”, “numero”, “codPostal”,
            “nombrepropio”}
        redis_connection : object
            conexión con la BD Redis con los registros T1
        """

        r_keys = redis_connection.keys(estructura + ':*')
        return [Region(estructura, str(reg.decode().split(':')[1])) for reg in r_keys]

    def subregiones(self, subestructura, r):
        """
        Devuelve todas las Regiones (nombres de región) que se
        correspondan con la subestructura especificada para la Region.

        Parameters
        ----------
        subestructura : str
            tipo de región. Valores posibles: {“estado”, “ca”, “provincia”,
            “comarca”, “municipio”, “nivel”, “tipovia”, “numero”, “codPostal”,
            “nombrepropio”}
        r : object
            conexión con la BD Redis con los registros T1
        """

        if self.estructura == 'nombrepropio':
            nom_subestructura = subestructura
            if nom_subestructura in ['via', 'municipio', 'provincia', 'ca', 'estado']:
                nom_subestructura = 'nombre' + nom_subestructura
            return [Region(subestructura, str(subreg[nom_subestructura])) for subreg in
                    decode_json(r.get(self.estructura + ':' + self.nombre))]

        r_keys_json = r.get(self.estructura + '_' + subestructura + ':' + self.nombre)
        if r_keys_json is None:
            return []
        r_keys = decode_json(r_keys_json)
        return [Region(subestructura, str(subreg)) for subreg in r_keys]

    def nombres(self):
        """
        Devuelve una lista con los posibles nombres derivados de la
        Region.
        """
        nombres = []

        for nombre_sub_bar in self.nombre.split('/'):
            if len(nombre_sub_bar.split('(')) == 2:
                nombres.extend([nombre_sub_bar.split('(')[0][:-1],
                                nombre_sub_bar.split('(')[1][:-1] + ' ' + nombre_sub_bar.split('(')[0][:-1]])
            elif len(nombre_sub_bar.split(',')) == 2:
                nombres.extend([nombre_sub_bar.split(',')[0],
                                nombre_sub_bar.split(',')[1][1:] + ' ' + nombre_sub_bar.split(',')[0]])

        if len(nombres) == 0:
            nombres = [self.nombre]

        return nombres

    def elementos(self, r):
        """
        Devuelve una lista con los elementos región almacenados en la
        base de datos (en formato JSON) cuyo nombre es el de la Region.

        Parameters
        ----------
        r : object
            conexión con la BD Redis con los registros T1
        """

        return decode_json(r.get(self.estructura + ':' + self.nombre))

    def __repr__(self):
        if self.confianza is not None:
            return 'Región (' + self.estructura + '): ' + self.nombre + ' (' + str(self.confianza * 100) + '%)'
        else:
            return 'Región (' + self.estructura + '): ' + self.nombre

    def __str__(self):
        return self.__repr__()

    def __eq__(self, reg):
        if type(reg) != Region:
            return False
        return self.estructura == reg.estructura and (self.nombre in reg.nombres() or reg.nombre in self.nombres())

    def __hash__(self):
        return hash(self.estructura + self.nombre)

    def __copy__(self):
        return Region(self.estructura, self.nombre, self.confianza, self.match)


class RegionVacia(Region):
    """
    Representa el conjunto de nombres asociados a una determinada
    estructura en la base de datos en su estado actual independientemente de su fecha
    de creación. No debemos confundir este concepto con el conjunto de todas las
    Regiones posibles, ya que entonces podríamos pensar que la función que calcula
    las subregiones de una RegionVacia devolvería otra RegionVacia, y no es así.

    Attributes
    ----------
    estructura : str
        tipo de región. Valores posibles: {“estado”, “ca”, “provincia”,
        “comarca”, “municipio”, “nivel”, “tipovia”, “numero”, “codPostal”,
        “nombrepropio”}
    """

    def __init__(self, estructura):
        Region.__init__(self, estructura, '*')

    def subregiones(self, subestructura, r):
        """
        Devuelve todas las Regiones (nombres de región) que sean
        subregiones de alguna región de la base de datos.

        Parameters
        ----------
        subestructura : str
            tipo de región. Valores posibles: {“estado”, “ca”, “provincia”,
            “comarca”, “municipio”, “nivel”, “tipovia”, “numero”, “codPostal”,
            “nombrepropio”}
        r : object
            conexión con la BD Redis con los registros T1
        """

        return Region.regiones(subestructura, r)

    def __eq__(self, reg):
        if type(reg) != RegionVacia:
            return False
        return self.estructura == reg.estructura

    def __copy__(self):
        return RegionVacia(self.estructura)