from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Estamos haciendo override del modelo del otro módulo, agregando un metodo también con override.
# La idea es linkear el campo sales_id del otro modelo, a un usuario en res.partner de forma obligatoria.
class EstateProperty(models.Model):

    # Si quisieramos heredar también los métodos y campos habría que colocar _name="estate.property"
    # Pero lo mantenemos simple solo indicando _inherit y especificando el campo sales_id
    _inherit = "estate.property" #Heredado

    sales_id = fields.Many2one("res.users", required=True)

    # Esto hace override del metodo del módulo original.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sales_person_property_ids = self.env[self._name].search_count([("sales_id", "=", vals.get("sales_id"))])
            print(sales_person_property_ids)
            if sales_person_property_ids >= 2:
                # Nos aseguramos que un máximo de dos propiedades se asignan a un vendedor
                raise ValidationError("User already has 2 properties assigned to themselves")

        # Este super llama al create del modulo original, es opcional (si no esta, simplemente reemplaza metodo)
        return super(EstateProperty, self).create(vals_list)