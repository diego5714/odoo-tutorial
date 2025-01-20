{
    'name': "Real estate tutorial",
    'version': "1.0",
    'description': """
        Real estate module for tutorial
    """,
    'category': "Sales",

    #base_setup permite que el código js con owl usado para crear una custom Client Action funcione.
    'depends': ["base", "base_setup", "mail", "website"],
    'data': [
        #groups
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/model_access.xml',
        'security/ir_rule.xml',

        #views
        'views/property_type_view.xml',
        'views/property_tags_view.xml',
        'views/property_offer_view.xml',
        'views/property_view.xml',
        'views/menu_items.xml',
        'views/property_web_template.xml',
        
        #Data:
        'data/property_type.xml',

        #Report:
        'report/property_report.xml',
        'report/report_template.xml'

    ],
    'demo': [
        'demo/property_tags.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'real_estate_tutorial/static/src/js/my_custom_tag.js',
            'real_estate_tutorial/static/src/xml/my_custom_tag.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': "LGPL-3"
}