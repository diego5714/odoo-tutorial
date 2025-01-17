from odoo import fields, models, api, _


class Property(models.Model):
    # Definimos una tabla/modelo en database para almacenar edificios o propiedades.
    # Existen tres tipos de modelos: Abstracto, Transiente y Regular
    # models.AbstractModel, models.TransientModel, models.Model

    # Los abstractos sirven para ser heredados, y permiten definir atributos comunes
    # La herencia se da mediante el atributo _inherit = ['nombre_modelo_abstracto']
    # No crea un modelo en la base de datos, solo sirve para ser heredado.

    # Los transientes son modelos que son para uso temporal. Una vez que cumplen la función que debían
    # realizar, son eliminados de memoria. Se usan por ejemplo en los diálogos para subir archivos con
    # datos adicionales

    # El siguiente es un modelo regular simplemente

    _name = 'estate.property' # Define estate_property en la database
    _description = 'Estate properties'

    # Los mixins son modelos abstractos que proveen funcionalidad útil a través de herencia
    # No tienen representación en la db.
    # Vamos a importar el mixin mail.thread, que permite tener un chatter o hilo de conversación.
    # También importamos mixing que permite llevar cuenta de actividades realizadas por usuarios.

    # utm.mixin permite interactuar y llevar cuenta de los cookies de los visitantes a nuestro app.
    # añande campos 'campaign', 'source' y 'medium' (Qué campaña publicitaria los trajo, desde donde, y en que medio)

    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    # Ahora agregamos campos a este modelo/tabla
    name = fields.Char(string = "Name", required = True)

    # Creamos un ManyToOne field para asociar una instancia de
    # modelo de property a una instancia del modelo de property_type
    # Por convención los manyToOne field tienen prefijo _id

    # Piensalos como que tu propiedad puede elegir de entre muchos valores de tipo, pero solo toma uno.

    # También se puede pensar como que un type puede estar asociado a multiples property,
    # Pero un property solo puede estar asociado a un único type
    # type_id -> Many -> property
    # property -> one -> type

    type_id = fields.Many2one('estate.property.type', string = "Property Type")

    # Creamos un ManyToMany field para asociar una instancia de modelo de property
    # a multiples entradas de property_tag
    # llevan prefijo _ids por convención

    # Piensalos como que tu propiedad puede elegir de entre muchos valores de tag,
    # y puede tomar multiples de ellos.

    # También se puede pensar como que un tag puede estar asociado a multiples property,
    # y un property puede estar asociado a múltiples tags.
    # tag -> Many -> property
    # property -> Many -> tag

    tag_ids = fields.Many2many('estate.property.tags', string = "Property Tags")

    description = fields.Text(string = "Description")
    postcode = fields.Char(string = "Postcode")
    date_availability = fields.Date(string = "Available From")

    # El atributo tracking permite que el mixing de mail.thread lleve la cuenta de cambios, a través del chatter
    expected_price = fields.Monetary(string = "Expected Price", tracking=True)
    best_offer = fields.Monetary(string="Best Offer")
    selling_price = fields.Monetary(string = "Selling Price")
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)

    bedrooms = fields.Integer(string = "Bedrooms")
    living_area = fields.Integer(string = "Living Area (sqm)")
    facades = fields.Integer(string = "Facades")
    garage = fields.Boolean(string = "Garage", default = False)
    garden = fields.Boolean(string="Garden", default = False)
    garden_area = fields.Integer(string = "Garden Area (sqm)")
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], string = "Garden Orientation"
    )

    # Creamos un One2many field para asociar una misma instancia de modelo de property
    # a múltiples instancias de ofertas. Sin embargo, con la restricción de que cada
    # oferta solo podrá estar asociada a un único property

    # La sintaxis es One2many(modelo, atributo conectado/inverso en ese modelo)

    offer_ids = fields.One2many('estate.property.offer', 'property_id', string = "Offers")

    sales_id = fields.Many2one('res.users', string="Salesman")

    # con domain podemos filtrar que tipo de elementos son seleccionables para el field
    # Por ejemplo aqui excluimos las entradas que son empresas

    buyer_id = fields.Many2one('res.partner', string="Buyer", domain = [('is_company', '=', False)])

    # Este siguiente campo será asignado como un "computed field" que ejecuta lógica
    # Para ello se debe definir una función y un decorador sacado desde api, que indica los requisitos

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    # Otra forma de definir cambios por lógica es con el decorador @api.onchange en vez de @api.depends.
    # Al usar esto ya no es necesario loopear en record, sino que la lógica se gatilla ante algún cambio.
    # Además, no es necesario agregar "compute = ..."

    # Ojo que este metodo sólo funciona para el scope dentro de un formulario. Si estás fuera del formulario,
    # esto no funciona. Suele ser preferible compute.
    """
    @api.onchange('living_area', 'garden_area')
    def _onchange_total_area(self):
        self.total_area = self.living_area + self.garden_area
    """
    #Computamos el numero de ofertas asociadas
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    offer_count = fields.Integer(string = "Offer Count", compute = _compute_offer_count)

    #####################################################################################
    # Ejemplo de como se puede cargar la vista de ofertas asociadas con type="object" en el xml

    def action_property_view_offers(self):
        # Aquí definimos una acción desde python en vez de xml

        # Especificar un dominio nos permite filtrar para que solo salgan las ofertas
        # asociadas a la propiedad visualizada actualmente
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name} - Offers",
            'domain': [('property_id', '=', self.id)],
            'view_mode': 'tree',
            'res_model': 'estate.property.offer'
        }
    #####################################################################################

    total_area = fields.Integer(string = "Total Area", compute = _compute_total_area)

    # Queremos mostrar el télefono del buyer cuando este es seleccionado en Many2one field.
    # para eso usamos un related field para referenciar a otro atributo del mismo tipo
    # que puede encontrarse en alguno de los atributos del archivo

    # En este caso relacionamos phone al atributo phone de buyer_id, el cual es una referencia a otro modelo
    phone = fields.Char(string = "phone", related = 'buyer_id.phone')
    # Análogo para email
    email = fields.Char(string = "e-mail", related = 'buyer_id.email')

    #########################################################################################################

    state = fields.Selection([
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], default = 'new', string = 'Status', group_expand='_expand_state')
    #group expand expande atributos kanban, aunque no haya records. Hace aparecer botón de crear

    # Estos métodos serán llamados desde la vista para cambiar state
    def action_sold(self):
        self.state = 'sold'

    def action_cancel(self):
        self.state = 'cancelled'

    ##############################################################################################

    # Metodo que permite llamar a una Client Action desde el menú, específicamente para mostrar una
    # notiicación. Este metodo es llamado por una acción, y devuelve un diccionario.

    # hay distintos tags predefinidos ya asociados a widgets, por ejemplo 'reload' o 'display_notification'
    def action_client_action_notify(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Testing client actions'),
                'type': 'success', #podria también ser 'warning' o 'danger'
                'sticky': False
            }
        }

    # Metodo que permite llamar a una url action, que nos permite acceder a una url
    def action_url_action(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.odoo.com',
            # Puede ser new, que lo abre en una nueva pestaña, o self, para utilizar la misma.
            'target': 'new'
        }
    #############################################################################################

    # Definimos métodos para la creación de reportes pdf, llamados desde report/property_report.xml

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Estate Property - %s' % self.name

    #############################################################################################

    # Este metodo permite expandir las categorías de la vista kanban, aunque no haya records.
    # esto permite acceder al botón de creación en esta vista, aún cuando no hay records.
    def _expand_state(self, states, domain, order):
        return [
            key for key, dummy in type(self).state.selection
        ]

    ##############################################################################################

