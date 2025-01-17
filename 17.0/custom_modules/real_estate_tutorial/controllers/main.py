from odoo import http
from odoo.http import request

# Podemos heredar y extender controladores de este u otros modulos importando el archivo .py
# y heredando de eso en vez de heredar de http.Controller al crear la clase

class PropertyController(http.Controller):

    # Definimos una ruta html a la que podemos acceder, gestionada por este controlador
    # similar al funcionamiento de django
    @http.route(['/properties'], type='http', website=True, auth="public")
    def show_properties(self):
        property_ids = request.env['estate.property'].sudo().search([])
        print(property_ids)

        # Devolvemos template de vista a renderizar, con id="property_list".
        # property_ids será una variable visible para la vista, con la que operaremos
        return request.render("real_estate_tutorial.property_list", {"property_ids": property_ids})