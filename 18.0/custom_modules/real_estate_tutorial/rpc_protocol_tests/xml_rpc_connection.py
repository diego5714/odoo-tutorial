# El protocolo xml-rpc permite que un programa externo interactúe con odoo, transmita y reciba información y ejecute métodos
# xml-rpc usa xml para codificar sus llamadas y html como mecanismo de transporte
# Este script es un ejemplo de uso de una librería xml-rpc en python para interactuar con odoo y nuestro módulo.

import xmlrpc.client

url = 'http://localhost:8069'
username = 'admin'
password = 'admin'
db = 'odoo_17_dev_db'

# Establecemos una primera comunicación, sin autenticación en este endpoint de odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

# A partir de esta conexión no autenticada podemos obtener algunos metadatos como la versión del server de odoo
#print(common.version())

# Ahora autenticamos la conexión mediante un usuario de odoo, en este caso el admin
user_uid = common.authenticate(db, username, password, {})
print("User UID: ", user_uid) # Esta operación nos devuelve el uid del usuario autenticado (2)

# Usamos ahora otro endpoint, que si requiere autenticación 'xmlrpc/2/object'
# en este endpoint podemos llamar al comando 'execute_kw' que recibe 'db, uid, password, model_name, method_name, [], {}'

models = common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search function
property_ids = models.execute_kw(db, user_uid, password, 'estate.property', 'search', [[]]) # el [] exterior es lista de parametros.
print("Search function ==> ", property_ids)

# Search function con paginación
pag_property_ids = models.execute_kw(db, user_uid, password, 'estate.property', 'search', [[]], {'offset': 0, 'limit': 2})
# Esta paginación nos muestra la página partiendo desde el offset 0, y con dos elementos en ella.
print("Search function with pagination ==> ", pag_property_ids)

# Count function
count_property_ids = models.execute_kw(db, user_uid, password, 'estate.property', 'search_count', [[]])
print("Count function ==> ", count_property_ids)

# Read function
read_property_ids = models.execute_kw(db, user_uid, password, 'estate.property', 'read', [property_ids], {'fields': ['name']})
print("Read function ==> ", read_property_ids)

# Search and read function
search_read_property_ids = models.execute_kw(db, user_uid, password, 'estate.property', 'search_read', [[]], {'fields': ['name']})
print("Search and read function ==> ", search_read_property_ids)

# Create function
"""
create_property_id = models.execute_kw(db, user_uid, password, 'estate.property', 'create', [{'name': 'Property from RPC', 'sales_id': 2}])
print("Create property ==> ", create_property_id)
"""

# Write function
write_property_id = models.execute_kw(db, user_uid, password, 'estate.property', 'write', [[15], {'name': 'Property from RPC (Updated)'}])
read_name_get = models.execute_kw(db, user_uid, password, 'estate.property', 'name_get', [[15]])
print("Write property ==> ", read_name_get)

# Unlink function
"""
unlink_property_id = models.execute_kw(db, user_uid, password, 'estate.property', 'unlink', [[14]])
print("Unlink property ==> ", unlink_property_id)
"""