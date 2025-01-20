{
    'name': "Real estate tutorial - For sales Person",
    'version': "1.0",
    'description': """
        Real estate module for tutorial on module inheritance (from our other real estate module)
        
        Links properties with a salesman in res.partner, extending real_estate_tutorial module with this.
    """,
    'category': "Sales",

    # base_setup permite que el código js con owl usado para crear una custom Client Action funcione.
    'depends': ["real_estate_tutorial", "base"],
    'data': [
        "views/res_users.xml"
    ],
    'installable': True,
    'application': False, # No es una app completa, sólo vamos a extender de la otra app
    'license': "LGPL-3"
}