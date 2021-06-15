# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Restrict Pricelist",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
	 "summary": """

 Restrict Pricelist,  Pricelist Security App, Pricelist Allocation Module, User Pricelist, Pricelist Visiblity Odoo.

                   """,
    "description": """
 Currently in odoo users can see all the pricelist with price details. so do you want different restrictions on the pricelist for different users? So here we build a module that can help to display specific pricelist to the user.How did it work? you need to go inside the particular user and select pricelist, which pricelist you want to visible for that user. if you don't give any pricelist than all pricelist will be accessible/visible. supposed you have selected some pricelist than only that selected pricelist will be accessible. wherever the pricelist field of view it will affect to all those fields. Cheers!


 Restrict Pricelist In Odoo.
 User Wise Access Price list In Odoo ,  Feature Of Manage User Wise Pricelist ,Allocate Pricelist In User Module, Show Specific Pricelist To Users.
  Pricelist Security App, Pricelist Allocation Module, User Pricelist, Pricelist Visiblity Odoo.

                   """,
    "version": "13.0.2.0",
    "depends": ['base', 'sale', 'sale_management'],
    "application" : True,
    "data": [
        'views/res_users_inherit_view.xml',
    ],

    "images": ["static/description/background.jpg", ],
    "live_test_url": "https://www.youtube.com/watch?v=hKmKGWSlmQE&feature=youtu.be",
    "auto_install": False,
    "installable" : True,
    "price": 25,
    "currency": "EUR"

}
