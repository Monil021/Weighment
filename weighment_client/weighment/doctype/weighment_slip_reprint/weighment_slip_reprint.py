# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.utils.data import format_date
import requests
from weighment_client.api import get_value
from escpos import *
from escpos.printer import Usb


class WeighmentSlipReprint(Document):
	@frappe.whitelist()
	def get_print (self):
		
		d_status = get_value(
			doctype = "Weighment",
			docname= self.enter_weighment_id,
			fieldname="docstatus",
			filters=({"name":self.enter_weighment_id})

		)
		if d_status and d_status == 2:
			frappe.throw("Not allow to print, This document is not submitted")
		
		profile = frappe.get_single("Weighment Profile")
		headers = {
				'Content-Type': 'application/json',
				"Authorization": f"token {profile.get('api_key')}:{profile.get_password('api_secret')}"
			}
		payload = json.dumps({"doctype": "Weighment","docname":self.enter_weighment_id})
		path = f"{profile.get('weighment_server_url')}/api/method/weighment_server.api.get_doctype_data_with_child_tables"

		response = requests.post(url = path, data = payload, headers = headers)
		if response.status_code == 200:
			response = response.json()
			if "message" in response:
				data = frappe.parse_json(response["message"])
				if data:
					print("Data:------>",data.get("items"))
					self.get_second_print(data)

					return True
		else:
			return False
		
	
	@frappe.whitelist()
	def get_second_print(self, data):
		profile = frappe.get_single("Weighment Profile")

		if profile.enable_printing:
			vid = int(profile.get("vendor_id"), 16)
			pid = int(profile.get("product_id"), 16)

			allowed_prints = 1

			try:
				if data.entry_type == "Outward" and data.delivery_note_details:
					item = data.get('delivery_note_details')[0].get('item')
					if item:
						if get_value(
							doctype="Item",
							docname=item,
							fieldname="custom_allow_duplicate_print",
							filters=({"name":item})
						) == 1:
							allowed_prints = 2
				
				if data.entry_type == "Inward" and data.items:
					item = data.get('items')[0].get('item_code')
					if get_value(
							doctype="Item",
							docname=item,
							fieldname="custom_allow_duplicate_print",
							filters=({"name":item})
						) == 1:
							allowed_prints = 2
			except:
				frappe.log_error(frappe.get_traceback(),"get's issue while checking allowed duplicate prints for weighment {}".format(data.name))

			if vid and pid:
				for _ in range(allowed_prints):
					try:                                
						p = Usb(vid, pid)
						
						p.open()
						
						def center_text(text, width):
							spaces = (width - len(text)) // 2
							return ' ' * spaces + text + ' ' * spaces
						
						header = center_text(f"{data.company} ({data.branch})", 40)
						p.text('\x1b\x21\x10' + '\x1b\x45\x01' + header + '\x1b\x45\x00' + '\x1b\x21\x00' + '\n')  # \x1b\x21\x10 for double-height and \x1b\x45\x01 for underline
						p.text(center_text("Weighment Slip", 40) + '\n')
						p.text(center_text(f"Weighment Date: {format_date(data.weighment_date)}", 40) + '\n')
						p.text('-' * 40 + '\n')

						lines = [
							f"Entry Type : {data.entry_type}   Branch : {data.branch}",

						]
						if data.supplier_name:
							lines.extend([
								f"Party Name : {data.supplier_name}",
							])

						if data.vehicle_type and data.vehicle_number:
							lines.extend([
								f"Vehicle Type : {data.vehicle_type}   Vehicle No : \x1b\x45\x01{data.vehicle_number}\x1b\x45\x00",
							])

						if data.vehicle_owner == "Third Party":
							lines.extend([
									f"Transporter : \x1b\x45\x01{data.transporter_name}\x1b\x45\x00",
								])
						
						if data.entry_type == "Inward":
							if not data.is_manual_weighment and data.get('items') and (len(data.get('items')) == 1):

								lines.extend([
									f"Item Group : \x1b\x45\x01{data.get('items')[0].get('item_group')}\x1b\x45\x00",
								])
							if not data.is_manual_weighment and data.get('items') and (len(data.get('items')) > 1):

								lines.extend([
									f"Item Name : \x1b\x45\x01Miscellaneous Item\x1b\x45\x00",
								])

							lines.extend([
								f"Inward Date : {format_date(data.inward_date)}   Gross Weight : \x1b\x45\x01{data.gross_weight} K \x1b\x45\x00",
								f"Outward Date : {format_date(data.outward_date)}   Tare Weight : \x1b\x45\x01{data.tare_weight} K \x1b\x45\x00",
							])
						
						if data.entry_type == "Outward":
							if not data.is_manual_weighment and data.item_group:

								lines.extend([
									f"Item Group : {data.item_group}",
								])
							
							lines.extend([
								f"Inward Date : {format_date(data.inward_date)}   Tare Weight : {data.tare_weight} K",
								f"Outward Date : {format_date(data.outward_date)}  Gross Weight : {data.gross_weight} K",
								
							])

						
						

						for line in lines:
							p.text(line + '\n')
						
						p.text('\x1b\x21\x10\x1b\x45\x01' + f"Net Weight : {data.net_weight} K" + '\x1b\x45\x00\x1b\x21\x00' + '\n')  # Double-height and underline

						p.text('-' * 40 + '\n')

						p.cut()

						frappe.msgprint(
							title="Printing...",
							indicator="orange",
							alert=True,
							realtime=True,
							msg="Collect Print"
						)

					except Exception as e:
						frappe.log_error(frappe.get_traceback(),"Getting second print error for weighment {} ".format(data.name))
					
					finally:
						p.close()
		return True
