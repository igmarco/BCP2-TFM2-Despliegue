from utiles import decode_json

class Region:
    def __init__(self, estructura, nombre, confianza=None, match=None):
        self.estructura = estructura
        self.nombre = nombre
        self.confianza = confianza
        self.match = match

    @staticmethod
    def regiones(estructura, redis_connection):
        r_keys = redis_connection.keys(estructura + ':*')
        return [Region(estructura, str(reg.decode().split(':')[1])) for reg in r_keys]

    def subregiones(self, subestructura, r):
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
    def __init__(self, estructura):
        Region.__init__(self, estructura, '*')

    def subregiones(self, subestructura, r):
        return Region.regiones(subestructura, r)

    def __eq__(self, reg):
        if type(reg) != RegionVacia:
            return False
        return self.estructura == reg.estructura

    def __copy__(self):
        return RegionVacia(self.estructura)