# Estructuras existentes.
estructuras = ['estado',
               'tipovia',
               'nombrepropio',
               'ca',
               'provincia',
               'comarca',
               'municipio',
               'nivel',
               'via',
               'codPostal',
               'numero']

# Superestructuras (ordenadas jerárquicamente) para cada estructura.
superestructura = {'ca':['estado'],
                   'provincia':['ca'],
                   'comarca':['provincia'],
                   'municipio':['provincia', 'comarca'],
                   'nivel':['municipio'],
                   'via':['municipio', 'nivel'],
                   'codPostal':['via'],
                   'numero':['via'],
                   }

# Subestructura de cada estructura (la inmediatamente siguiente en la cadena).
subestructura = {'estado':'ca',
                 'ca':'provincia',
                 'provincia':'comarca',
                 'comarca':'municipio',
                 'municipio':'nivel',
                 'nivel':'via',
                 'via':'codPostal',
                 'codPostal':'numero'
                  }

# Dependencias de ciertas estructuras (de pasos iniciales).
dependencia = {'estado':['nombrepropio'],
               'ca':['nombrepropio'],
               'provincia':['nombrepropio'],
               'municipio':['nombrepropio'],
               'via':['tipovia', 'nombrepropio'],
               'codPostal':['nombrepropio'],
               'numero':['nombrepropio']
               }

# Pasos que pueden obviarse en la cadena de la dirección.
pasos_opcionales = ['comarca', 'nivel', 'codPostal', 'numero']

# Pasos que conviene que se evalúen al principio del todo.
pasos_iniciales = ['estado', 'tipovia', 'nombrepropio']

# Estructura de origen.
origen = 'estado'