# -*- coding: utf-8 -*-
# ©  2015-2020 Deltatech
# See README.rst file on addons root folder for license details


class AbstractProvider():

    def __init__(self, prod_environment, debug_logger):
        """  se face initializarea obiectului """
        pass

    def login(self, credentials):
        """ Credentialele pentru acesul serviciului web"""
        self.credentials = credentials

    def call_method(self, function, parameters=None, verb='GET', files=None):
        """ Apelul efecti a reviciului web """
        raise NotImplementedError()

    def get_shipping_price(self, shipment_info):
        """ Obtine pretul in in baza datelor din shipment_info"""
        raise NotImplementedError()

    def send_shipping(self, shipment_info):
        """ Se trimit datele din shipment_info si se obtine un dict in care se gaseste tracking_number  """
        raise NotImplementedError()

    def get_label(self, tracking_ref, type=None, format=None):
        raise NotImplementedError()

    def save_label(self):
        """Convert label to base64"""
        raise NotImplementedError()

    def cancel_shipment(self, tracking_number):
        """ anulare AWB"""
        raise NotImplementedError()
