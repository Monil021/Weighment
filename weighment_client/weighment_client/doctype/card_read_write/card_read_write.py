# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form
import requests
from weighment_client.api import get_child_table_data_for_single_doctype, get_document_names, get_value
from weighment_client.weighment_client_utils import read_smartcard
from frappe.frappeclient import FrappeClient
class CardReadWrite(Document):

    @frappe.whitelist()
    def read_data(self):
        data = read_smartcard()
        if data:
            val = frappe.get_value("Card Details",{"hex_code":data},["card_number","status"])
            if val:
                self.card_number, self.status = val
            if not val:
                self.card_number = 0
                self.status = "Blank"
    
    @frappe.whitelist()
    def write_data(self):
        if self.card_number:
            data = read_smartcard()
            profile = frappe.get_cached_doc("Weighment Profile")
            if not frappe.get_value("Branch Table",{"is_primary":1},["branch"]):
                frappe.throw(f"Please update Primary branch in {get_link_to_form('Weighment Profile','Weighment Profile')}")
            if not profile.location:
                frappe.throw(f"Please update location in {get_link_to_form('Weighment Profile','Weighment Profile')}")
            if data:
                val = frappe.get_value("Card Details",{"hex_code":data},["card_number"])
                if val:
                    doc = frappe.get_cached_doc("Card Details", val)
                    if doc.is_assigned:
                        frappe.throw("Not allow to change card number, This card is already in use...")
                    else:
                        doc.card_number = self.card_number
                        doc.save(ignore_permissions=True)
                else:
                    doc = frappe.new_doc("Card Details")
                    doc.card_number = self.card_number
                    doc.hex_code = data
                    doc.branch = frappe.get_value("Branch Table",{"is_primary":1},["branch"]) #profile.get("branch")
                    doc.location = profile.get("location")
                    doc.status = "Issued"
                    doc.save(ignore_permissions=True)

        else:
            frappe.throw("Please enter card number first")

    @frappe.whitelist()
    def generate_number(self):
        # PROFILE = frappe.get_doc("Weighment Profile")
        data = get_child_table_data_for_single_doctype(parent_docname="Naming Setting For Smart Card",child_table_fieldname="smartcard_numbering_details")
        for d in data:
            if d.get("branch") == frappe.get_value("Branch Table",{"is_primary":1},["branch"]):
                present_counter = d.get("counter").split("-")
                abbr = present_counter[0]
                counter = present_counter[1]
                new_counter = str(abbr + "-" + str(int(counter)+1))
                self.card_number = new_counter
                self.status = "Blank"
