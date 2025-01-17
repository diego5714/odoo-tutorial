from odoo import fields, models


class PropertyTag(models.Model):
    _name = 'estate.property.tags'
    _description = "Property Tags"

    name = fields.Char(string = "Name", required = True)