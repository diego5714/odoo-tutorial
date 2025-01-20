from odoo import fields, models


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Property Type"

    name = fields.Char(string = 'Name', required = True)