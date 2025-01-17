from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'

    price = fields.Monetary(string = "Price", required = True)
    currency_id = fields.Many2one("res.currency", string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    status = fields.Selection(
        [('accepted', 'Accepted'), ('rejected', 'Rejected')], string="Status"
    )

    ###################################################################################################
    # El modelo res.partner es parte de odoo (módulo base), representa a un cliente
    # Cada cliente puede asociarse a varias ofertas, pero cada oferta solo se asocia a un unico cliente.

    # Recordar que si se usa un módulo externo se debe agregar a depends en el manifest.

    #Tenemos múltiples customers a elegir, pero nos quedamos solo con uno

    partner_id = fields.Many2one('res.partner', string = "Customer")

    ###################################################################################################
    # Linkeamos la oferta a una única propiedad. Cada propiedad podrá asociarse a varias ofertas,
    # Pero cada oferta solo se puede asociar a una única propiedad

    #Tenemos múltiples propiedades a elegir y nos quedamos solo con una.
    property_id = fields.Many2one('estate.property', string = "Property")

    ###################################################################################################

    validity = fields.Integer(string = "Validity (days)")

    # El decorador api.model se usa cuando el self sobre el que se itera es un record de algún modelo,
    # y no nos importa su contenido, solo el modelo.

    # En este ejemplo, no iteramos sobre el contenido, solo devolvemos la fecha actual
    # No es el mejor ejemplo porque se podría hacer sin el decorador, pero se entiende la idea.
    # El metodo se establece como default en el campo de creation date

    @api.model
    def _set_create_date(self):
        return fields.Date.today()

    creation_date = fields.Date(string = "Creation Date", default = _set_create_date)

    ####################################################################################################

    @api.depends('validity', 'creation_date')
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + timedelta(days = rec.validity)
            else:
                rec.deadline = False

    def _inverse_deadline(self):
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
            else:
                rec.validity = False

    # Aplicar logica por compute se hace de forma instantánea ante cambios en las entradas
    # En cambio, al aplicar lógica por inverse, el cambio sólo se hace al guardar manualmente el formulario

    # La función inversa propaga cambios hacia atrás sólamente tras guardar de forma manual

    deadline = fields.Date(string="Deadline", compute = _compute_deadline, inverse = _inverse_deadline)

    # Computamos el nombre de la oferta a partir de cliente y propiedad
    @api.depends('property_id', 'partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.property_id and rec.partner_id:
                rec.name = f"{rec.property_id.name} - {rec.partner_id.name}"
            else:
                rec.name = False

    name = fields.Char(string = "Description", compute = _compute_name)

    ########################################################################################################
    ########################################################################################################

    # El decorador constraint nos permite imponer una restricción/constraint sobre un campo
    # a esto se le llama un constraint de python

    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline and rec.creation_date:
                if rec.deadline < rec.creation_date:
                    raise ValidationError("Creation date cannot be greater than deadline")
            elif not rec.deadline and rec.creation_date:
                raise ValidationError("Deadline cannot be the same as creation date")

    @api.constrains('deadline')
    def _check_date_end(self):
        for record in self:
            if record.deadline < fields.Date.today():
                raise ValidationError("The deadline cannot be set in the past")

    """     
    # Otra manera más simple, pero un poco menos flexible de imponer restricciones es usando constraints de sql.
    # Pueden requerir reinstalar el módulo para empezar a funcionar.
    
    _sql_constraints = [
        ('check_validity', 'check(validity > 0)', 'Deadline must be greater than creation date')
    ]
    """

    ###############################################################################################################

    # el decorador api.autovacuum permite que el servicio de cron autovacuum invoque a esta función automáticamente
    # Por ejemplo esta función elimina las ofertas rechazadas de forma automática
    """
    @api.autovacuum
    def _clean_offers(self):
        self.search([('status', '=', 'refused')]).unlink()
    """

    ###############################################################################################################
    ###############################################################################################################

    # Métodos ORM: Permiten manipular e interactuar con la base de datos.

    # create: Permite crear entradas en la db.
    # write: Permite hacer cambios en la db. Es llamado ante cualquier cambio o guardado (desde Interfaz)
    # delete (Unlink): Permite eliminar entradas en la db.
    # browse: Nos permite rescatar un record con un id específico

    # Las formas base de create y write (presentes en la superclase Model) reciben dos argumentos: self que
    # contiene el record o set de records con el que se está trabajando, y vals que es un diccionario que
    # contiene atributos de la entrada a crear/manipular (Pueden ser todos o solo algunos dependiendo del caso)

    # unlink simplemente se ejecuta mediante dispatch a un record-set
    # Ej: filtered_record_set.unlink()

    # browse y derivados hacen dispatch sobre un record completo, y reciben como parámetro un dominio y
    # algunas configuraciones.

    # Podemos hacer override de estas funciones para agregarles funcionalidad siempre que llamemos a super al
    # final para llamar a la función base.

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if not rec.get('creation_date'):
                rec['creation_date'] = fields.Date.today()

        # Esta línea simplemente llama al metodo create original en la clase padre de PropertyOffer (Model),
        # con el mismo set de records y el mismo vals.
        return super(PropertyOffer, self).create(vals)

    # La anterior función hace override de "create", y además como tiene el decorador "model_create_multi",
    # "vals" ahora es tratado como una lista de records con atributos cada uno, en vez de un diccionario
    # de atributos para un record individual, permitiéndonos operar sobre la creación de multiples entradas a la vez.
    #
    # La lógica simplemente agrega la fecha actual si las entradas que queremos crear en nuestro diccionario vals
    # no tienen fecha. Esto no es llamado desde la interfaz, solo actúa si lo llamamos nosotros con un diccionario

    ###################################################################

    def write(self, vals):
        # Imprimimos el record trabajado
        # vals solo incluye un diccionario con los atributos cambiados
        print(vals)

        # Podemos rescatar un record con un id específico con browse
        # notar que self.env nos permite acceder al entorno de ejecución y
        # tener acceso mapeado al registro de otros modelos, y a otro tipo de información.
        #
        # Esto no tiene por qué ir aquí, es solo para que se ejecute al guardar.
        res_partner = self.env['res.partner'].browse(1) #id 1
        print(res_partner.name)

        # Podemos buscar entradas en los records comparando ante un dominio o parámetros dados
        # esto nos devuelve un record-set que coincida.
        res_partners_4 = self.env['res.partner'].search([('is_company', '=', True)], limit = 4, order = 'name desc')

        print(res_partners_4)
        for partner in res_partners_4:
            print(partner.name)

        # Podemos devolver el número total de records en una búsqueda:
        print(
            self.env['res.partner'].search_count([('is_company', '=', True)]) # devuelve 8
        )

        # Podemos mapear un atributo de todos los records en el set a una lista (asi evitamos hacer un ciclo for)
        # Esto devuelve una lista con todos los teléfonos de cada entrada.
        print(
            res_partners_4.mapped('phone')
        )

        res_partners = self.env['res.partner'].search([('is_company', '=', True)])

        # Podemos aplicar un filtro mediante una función (anónima o definida) a un record-set
        # Esto devuelve las entradas que tienen número de teléfono
        partners_with_phone = res_partners.filtered(lambda x: x.phone)

        print(partners_with_phone)


        return super(PropertyOffer, self).write(vals)

    ###########################################################################################
    ###########################################################################################

    # Este metodo es llamado por una Server Action
    # extiende el deadline de los records seleccionados
    def extend_offer_deadline(self):
        active_ids = self._context.get('active_ids', [])
        if active_ids:
            # Lo siguiente nos devuelve un record set a partir de la lista de ids numericos
            offer_ids = self.env['estate.property.offer'].browse(active_ids)
            for offer in offer_ids:
                offer.validity += 1

    # Este metodo es llamado por un cronjob o Scheduled Action
    # Extiende los deadlines de todos los records en 1, una vez al dia
    def extend_offer_deadline_all(self):
        offer_ids = self.env['estate.property.offer'].search([])
        for offer in offer_ids:
            offer.validity += 1