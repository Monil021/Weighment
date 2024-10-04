# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

from datetime import datetime
import json
import time
import warnings
import frappe
from frappe.model.document import Document

from frappe.utils.data import (
	format_date, 
	get_datetime, 
	get_link_to_form, 
	getdate, 
	now, 
	today
)

import requests
from weighment_client.api import (
    get_allowed_tolerance, 
    get_gate_entry_data_from_card_number, 
    get_gate_entry_data_from_gate_entry, 
    get_item_data, 
    get_value, 
    get_weighment_data_from_card_number, 
    get_weighment_data_from_gate_entry, 
    is_new_weighment_record_for_weighment
)

from weighment_client.weighment_client_utils import (
    check_card_removed,
    google_voice, 
    play_audio,
    read_button_switch, 
    read_smartcard, 
    read_weigh_bridge
)

from escpos import *
from escpos.printer import Usb

class Weighment(Document):
	warnings.filterwarnings("ignore", category=DeprecationWarning)

	@frappe.whitelist()
	def check_weighbridge_is_empty (self):

		wake_up_weight = frappe.db.get_single_value("Weighment Profile","wake_up_weight")
		if not wake_up_weight:
			frappe.msgprint(
				title="Wakeup Weight Missing for Weigh Bridge",
				msg=f"Please Update Wakeup weight in {get_link_to_form('Weighment Profile','Weighment Profile')}",
			)
		while True:
			if read_weigh_bridge()[0] <= wake_up_weight:
				print("Weight gain detected...")
				return True
			
			else:
				play_audio(audio_profile="Please check platform is blank")
				time.sleep(2)

	
	@frappe.whitelist()
	def wake_up_screen (self):

		wake_up_weight = frappe.db.get_single_value("Weighment Profile","wake_up_weight")
		if not wake_up_weight:
			frappe.msgprint(
				title="Wakeup Weight Missing for Weigh Bridge",
				msg=f"Please Update Wakeup weight in {get_link_to_form('Weighment Profile','Weighment Profile')}",
			)
		while True:
			if read_weigh_bridge()[0] >= wake_up_weight:
				return True
			
			else:
				print("Waiting for weight gain...",read_weigh_bridge()[0])
				time.sleep(2)

	
	@frappe.whitelist()
	def fetch_card_details(self):
		while True:
			hex_code = read_smartcard(timeout=3)
			print("hex:--------------->",hex_code)
			if hex_code:
				return hex_code
			else:
				play_audio(audio_profile="Please put your card on machine")
				time.sleep(1)

	@frappe.whitelist()
	def check_card_validations(self, hex_code):
		print("hex code received:----->",hex_code)
		if hex_code:
			if frappe.db.exists("Card Details", {"hex_code": hex_code}):
				card_number = frappe.db.get_value("Card Details",{"hex_code":hex_code},["card_number"])

				if card_number:
					entry = get_gate_entry_data_from_card_number(card_number=card_number)
					if entry and "message" in entry:
						entry = entry["message"]
						if entry.get("is_completed"):
							return "weighment_already_done"
						
						if entry.get("is_manual_weighment"):
							self.is_manual_weighment = entry.get("is_manual_weighment")
						
						if entry.get("is_subcontracting_order"):
							self.is_subcontracting_order = entry.get("is_subcontracting_order")
						
						if entry.get("enable_weight_adjustment"):
							self.enable_weight_adjustment = entry.get("enable_weight_adjustment")
						
						if entry.get("entry_type") == "Outward" and entry.get("is_in_progress") and not entry.get("is_manual_weighment") and not entry.get("job_work"):
							weighment = get_weighment_data_from_card_number(card_number=card_number)

							if weighment and "message" in weighment:
								weighment = weighment["message"]

								if not weighment.get("delivery_note_details") and not weighment.get("is_manual_weighment"):
									return "trigger_empty_delivery_note_validation"
						
						if entry.get("name"):
							return {"gate_entry":entry.get("name")}
						
						else:
							return "trigger_empty_card_validation"
						
					else:
						return "trigger_empty_card_validation"

				else:
					return "trigger_empty_card_validation"

			else:
				return "trigger_empty_card_validation"


	@frappe.whitelist()
	def fetch_gate_entry(self):
		data = read_smartcard()

		if data:
			card_number = frappe.db.get_value("Card Details",{"hex_code":data},["card_number"])
			if not card_number:
				return "trigger_empty_card_validation"
			
			if card_number:
				entry = get_gate_entry_data_from_card_number(card_number=card_number)
				if entry and "message" in entry:
					entry = entry["message"]
					if entry.get("is_completed"):
						return "weighment_already_done"
					
					if entry.get("is_manual_weighment"):
						self.is_manual_weighment = entry.get("is_manual_weighment")
					
					if entry.get("is_subcontracting_order"):
						self.is_subcontracting_order = entry.get("is_subcontracting_order")
					
					if entry.get("enable_weight_adjustment"):
						self.enable_weight_adjustment = entry.get("enable_weight_adjustment")

					
					if entry.get("entry_type") == "Outward" and entry.get("is_in_progress") and not entry.get("is_manual_weighment") and not entry.get("job_work"):
						weighment = get_weighment_data_from_card_number(card_number=card_number)

						if weighment and "message" in weighment:
							weighment = weighment["message"]

							if not weighment.get("delivery_note_details") and not weighment.get("is_manual_weighment"):
								return "trigger_empty_delivery_note_validation"

					if entry.get("name"):
						return {"gate_entry":entry.get("name")}
					
					else:
						return "trigger_empty_card_validation"

				else:
					return "trigger_empty_card_validation"
			else:
				return "trigger_empty_card_validation"
	
	@frappe.whitelist()
	def map_data_by_card (self):
		if self.gate_entry_number:
			meta = frappe.get_meta("Weighment")
			try:
				weighment = get_weighment_data_from_gate_entry(
					gate_entry = self.gate_entry_number
				)
				if weighment and "message" in weighment:
					data = weighment["message"]
					print("data1:------>",data)
					child_tables = {}
					for key, value in data.items():
						if isinstance(value, list) and all(isinstance(item, dict) for item in value):
							child_tables[key] = value
					

					for key, value in data.items():
						if key not in child_tables:
							if meta.has_field(key):
								self.set(key, value)
					
						
					for table_field, rows in child_tables.items():
						self.set(table_field, [])
						for row in rows:
							self.append(table_field, row)

					if not self.outward_date:
						self.outward_date = getdate(now())
					self.reference_record = data.get("name")

					
				else:
					gate_entry = get_gate_entry_data_from_gate_entry(
						gate_entry= self.gate_entry_number
					)
					if gate_entry and "message" in gate_entry:
						data = gate_entry["message"]
						print("data2:------>",data)
						child_tables = {}
						for key, value in data.items():
							if isinstance(value, list) and all(isinstance(item, dict) for item in value):
								child_tables[key] = value
						
						
						for key, value in data.items():
							if key not in child_tables:
								print("key:----->",key, "value:----->",value)
								if meta.has_field(key):
									self.set(key, value)
						
							
						for table_field, rows in child_tables.items():
							self.set(table_field, [])
							for row in rows:
								self.append(table_field, row)
				
				print("data processed !!!!")

				self.weighment_date = getdate(today())
				self.inward_date = get_datetime(now())

				if self.entry_type == "Outward" and not self.is_manual_weighment and not self.is_subcontracting_order and not self.job_work:
					
					allowed_lower_tolerance, allowed_upper_tolerance = self.get_allowed_tolerance_data(self.item_group, self.branch)
					self.allowed_lower_tolerance = allowed_lower_tolerance or 0
					self.allowed_upper_tolerance = allowed_upper_tolerance or 0

					if self.delivery_note_details:
						self.total_weight = sum(d.total_weight for d in self.delivery_note_details)
						self.minimum_permissible_weight = self.total_weight - self.allowed_lower_tolerance
						self.maximum_permissible_weight = self.total_weight + self.allowed_upper_tolerance

				return True
			
			except:
				return False

	@frappe.whitelist()
	def check_for_button(self):
		while True:
			response = read_button_switch(timeout=2)
			print("button switch:----------->",response)
			if response:
				play_audio(audio_profile="Button Press Detected")
				return response
			else:
				play_audio(audio_profile="Press green button for weight")
				time.sleep(1)

	@frappe.whitelist()
	def remove_card_from_machine (self):
		while True:
			response = check_card_removed(timeout=2)
			print("card remove responce:----->",response)
			if response:
				return response
			else:
				play_audio(audio_profile="Please remove your card")
				time.sleep(1)
			
	
	@frappe.whitelist()
	def validate_card_number(self):
		count = 0
		while count < 2:
			play_audio(audio_profile="Used Token")
			count +=1
			time.sleep(1)
		return True
			
	@frappe.whitelist()
	def empty_delivery_note_validatin(self):
		count = 0
		while count < 2:
			play_audio(audio_profile="contact_with_sales_department")
			count +=1
			time.sleep(1)

		return True

	@frappe.whitelist()
	def needs_reweighment(self):
		for _ in range(3):
			play_audio(audio_profile="needs_reweight")
			time.sleep(1)
		
		return True
	
	@frappe.whitelist()
	def get_allowed_tolerance_data(self,item_group,branch):
		data = get_allowed_tolerance(item_group=item_group,branch=branch)
		if data and "message" in data:
			data = data["message"]
			return data.get("allowed_lower_tolerance"),data.get("allowed_upper_tolerance")

		return None, None

	
	

	
	@frappe.whitelist()
	def is_new_weighment_record(self,args):
		if args.entry:
			try:
				data = is_new_weighment_record_for_weighment(
					gate_entry= args.entry
				)
				if data and "message" in data:
					data = data["message"]
					if data == "existing_weighment_record_found":
						return "existing_record_found"
					
					if data == "no_weighment_record_found":
						return "no_weighment_record_found"
					
					if data == "no_gate_entry_found":
						return "need_reweighment"
			except:
				return "need_reweighment"
	
	@frappe.whitelist()
	def update_weight_details_for_new_entry(self,args):
		data = frappe._dict()
		if args.entry:

			if self.entry_type == "Inward":
				self.gross_weight = read_weigh_bridge()[0]
				# time.sleep(5)
				play_audio(audio_profile="Your Gross Weight Is")

				quintal = str(int(self.gross_weight) / 100)
				kilogram = str(int(self.gross_weight) % 100)
				_quintal = (quintal.split("."))
				if "." in quintal:
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")

				# print(quintal,kilogram)
				# google_voice(text=quintal)

				# play_audio(audio_profile="Quintal")
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")
				
			if self.entry_type == "Outward":
				self.tare_weight = read_weigh_bridge()[0]
				# time.sleep(5)
				play_audio(audio_profile="Your Tare Weight Is")
				# if self.tare_weight < 100:
				quintal = str((int(self.tare_weight) / 100))
				_quintal = (quintal.split("."))
				if "." in quintal:
					print("@@@@@@@@@@@@@@@@@@Quintal",_quintal,type(_quintal))
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")
				
				kilogram = str((int(self.tare_weight) % 100))
				
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")

	
	@frappe.whitelist()
	def create_new_weighment_entry(self):
		try:
			profile = frappe.get_single("Weighment Profile")

			path = f"{profile.get('weighment_server_url')}/api/method/weighment_server.api.create_weighment"
			data = self.as_dict()
			data["is_in_progress"] = 1

			fields_to_check = ["driver","transporter","supplier"]

			for field in fields_to_check:
				if data.get(field) and "~" in data.get(field):
					field_value = data.pop(field)
					actual_value = field_value.split("~")[0]
					data[field] = actual_value

			
			payload = json.dumps({"data":data})

			headers = {
				'Content-Type': 'application/json',
				"Authorization": f"token {profile.get('api_key')}:{profile.get_password('api_secret')}"
			}

			response = requests.post(
				url = path,
				headers = headers,
				data = payload
			)

			

			print ("response :---->",response.text,response.status_code)

			response = response.json()

			print("************",response["message"])
			
			if response and "message" in response:
				response = response["message"]
				print("response:----->",response[0])
				self.get_first_print()
				return "weight_done"
			
			else:
				frappe.log_error(frappe.get_traceback(),"Gets error while creating weighment against gate entry {}".format(self.gate_entry_number))
				return "needs_reweight"

			
		except:
			frappe.log_error(frappe.get_traceback(),"Gets error while creating weighment against gate entry {}".format(self.gate_entry_number))
			return "needs_reweight"

	
	@frappe.whitelist()
	def update_weight_details_for_existing_entry(self):
		if self.reference_record:
			# rec = frappe.get_cached_doc("Weighment",self.reference_record)
			if self.entry_type == "Outward" and not self.tare_weight and not self.gross_weight:
				self.tare_weight = read_weigh_bridge()[0]
				
			if self.entry_type == "Outward" and self.tare_weight and not self.gross_weight:
				self.gross_weight = read_weigh_bridge()[0]

			if self.entry_type == "Inward" and not self.tare_weight and not self.gross_weight:
				self.gross_weight = read_weigh_bridge()[0]
			if self.entry_type == "Inward" and not self.tare_weight and self.gross_weight:
				self.tare_weight = read_weigh_bridge()[0]
			
			
			# time.sleep(3)
			if self.entry_type == "Inward" and self.tare_weight == 0:
				play_audio(audio_profile="Tare Not Done Yet")
				# play_audio(audio_profile="system_error")
				return "trigger_weight_validation"

			if self.gross_weight <= self.tare_weight:
				play_audio(audio_profile="Tare weight cant be less than gross weight")
				return "trigger_weight_validation"
			

			self.net_weight = self.gross_weight - self.tare_weight
			self.validate_purchase_weight()
			self.validate_sales_weight()
			if self.allowed_lower_tolerance > 0:

				if self.net_weight < self.minimum_permissible_weight:
					play_audio(audio_profile="Delivery Exception")
					return "trigger_delivery_note_validation"
			
			if self.allowed_upper_tolerance > 0:
				
				if self.net_weight > self.maximum_permissible_weight:
					play_audio(audio_profile="Delivery Exception")
					return "trigger_delivery_note_validation"

			if self.entry_type == "Outward":

				play_audio(audio_profile="Your Gross Weight Is")

				quintal = str(int(self.gross_weight) / 100)
				kilogram = str(int(self.gross_weight) % 100)
				
				if "." in quintal:
					_quintal = (quintal.split("."))
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")

				# print(quintal,kilogram)
				# google_voice(text=quintal)
				# play_audio(audio_profile="Quintal")
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")

				

				play_audio(audio_profile="Your Net Weight Is")
				quintal = str(int(self.net_weight) / 100)
				kilogram = str(int(self.net_weight) % 100)
				if "." in quintal:
					_quintal = (quintal.split("."))
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")


				# print(quintal,kilogram)
				# google_voice(text=quintal)
				# play_audio(audio_profile="Quintal")
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")

			if self.entry_type == "Inward":

				play_audio(audio_profile="Your Tare Weight Is")

				quintal = str(int(self.tare_weight) / 100)
				kilogram = str(int(self.tare_weight) % 100)
				if "." in quintal:
					_quintal = (quintal.split("."))
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")

				# print(quintal,kilogram)
				# google_voice(text=quintal)
				# play_audio(audio_profile="Quintal")
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")


				play_audio(audio_profile="Your Net Weight Is")
				quintal = str(int(self.net_weight) / 100)
				kilogram = str(int(self.net_weight) % 100)
				if "." in quintal:
					_quintal = (quintal.split("."))
					if _quintal:
						google_voice(text=_quintal[0])
						play_audio(audio_profile="Quintal")
				else:
					google_voice(text=quintal)
					play_audio(audio_profile="Quintal")

				# print(quintal,kilogram)
				# google_voice(text=quintal)
				# play_audio(audio_profile="Quintal")
				google_voice(text=kilogram)
				play_audio(audio_profile="KG")
				play_audio(audio_profile="Huva")

			return True

	@frappe.whitelist()
	def validate_purchase_weight(self):
		if self.entry_type == "Inward" and self.items and len(self.items)<=1 and not self.is_manual_weighment and not self.is_subcontracting_order:
			if self.enable_weight_adjustment:

				if self.net_weight < self.items[0].get("accepted_quantity"):
					for d in self.items:
						c_factor = frappe.db.get_value("UOM Conversion",{"uom":d.get("uom")},["conversion_factor"])
						if c_factor:
							d.accepted_quantity = self.net_weight/c_factor
							d.received_quantity = self.net_weight/c_factor

				if self.net_weight > self.items[0].get("accepted_quantity"):
					extra_weight = self.net_weight - self.items[0].get("accepted_quantity")
					self.gross_weight -= extra_weight
					self.net_weight -= extra_weight
					self.weight_adjusted = 1
			
			else:
				for d in self.items:
					c_factor = frappe.db.get_value("UOM Conversion",{"uom":d.get("uom")},["conversion_factor"])
					if c_factor:
						d.accepted_quantity = self.net_weight/c_factor
						d.received_quantity = self.net_weight/c_factor

	@frappe.whitelist()
	def update_existing_weighment_details (self):
		profile = frappe.get_single("Weighment Profile")
		if self.gate_entry_number and not ((self.gross_weight == self.tare_weight) or (self.gross_weight <= self.tare_weight)):
			if self.reference_record:
				data = self.as_dict()
				data["doctype"] = "Weighment"
				data["name"] = self.reference_record
				data["is_in_progress"] = False
				data["is_completed"] = True
				data["outward_date"] = datetime.strftime(get_datetime(now()), "%Y-%m-%d %H:%M:%S")

				fields_to_check = ["driver","transporter","supplier"]

				for field in fields_to_check:
					if data.get(field) and "~" in data.get(field):
						field_value = data.pop(field)
						actual_value = field_value.split("~")[0]
						data[field] = actual_value

				
				payload = json.dumps({"data":data})
				path = f"{profile.get('weighment_server_url')}/api/method/weighment_server.api.update_weighment"

				headers = {
					'Content-Type': 'application/json',
					"Authorization": f"token {profile.get('api_key')}:{profile.get_password('api_secret')}"
				}

				response = requests.post(
					url = path,
					headers = headers,
					data = payload
				)
				print("************",response.text)

				response = response.json()

				
				
				if response and "message" in response:
					response = response["message"]
					print("response:----->",response[0])
					self.get_second_print()
					return "weight_done"
				
				else:
					frappe.log_error(frappe.get_traceback(),"Gets error while creating weighment against gate entry {}".format(self.gate_entry_number))
					return "needs_reweight"

	@frappe.whitelist()
	def validate_sales_weight(self):
		if not self.is_manual_weighment and self.entry_type == "Outward" and self.delivery_note_details and self.is_in_progress:
			for d in self.delivery_note_details:
				if d.get("item"):
					item = get_item_data(item_code=d.get("item"))
					if item and "message" in item:
						item = item["message"]
						if item.get("custom_is_weighment_mandatory") and not (len(self.delivery_note_details) >=2):
							conversion = frappe.db.get_value("UOM Conversion",{"uom":d.get("uom")},["conversion_factor"])
							if conversion:
								d.qty = self.net_weight/conversion

	@frappe.whitelist()
	def get_second_print(self):
		profile = frappe.get_single("Weighment Profile")

		if profile.enable_printing:
			vid = int(profile.get("vendor_id"), 16)
			pid = int(profile.get("product_id"), 16)

			allowed_prints = 1

			try:
				if self.entry_type == "Outward" and self.delivery_note_details:
					item = self.delivery_note_details[0].get("item")
					if item:
						if get_value(
							doctype="Item",
							docname=item,
							fieldname="custom_allow_duplicate_print",
							filters=({"name":item})
						) == 1:
							allowed_prints = 2
				
				if self.entry_type == "Inward" and self.items:
					item = self.items[0].get("item_code")
					if get_value(
							doctype="Item",
							docname=item,
							fieldname="custom_allow_duplicate_print",
							filters=({"name":item})
						) == 1:
							allowed_prints = 2
			except:
				frappe.log_error(frappe.get_traceback(),"get's issue while checking allowed duplicate prints for weighment {}".format(self.reference_record))

			if vid and pid:
				for _ in range(allowed_prints):
					try:                                
						p = Usb(vid, pid)
						
						p.open()
						
						def center_text(text, width):
							spaces = (width - len(text)) // 2
							return ' ' * spaces + text + ' ' * spaces
						
						header = center_text(f"{self.company} ({self.branch})", 40)
						p.text('\x1b\x21\x10' + '\x1b\x45\x01' + header + '\x1b\x45\x00' + '\x1b\x21\x00' + '\n')  # \x1b\x21\x10 for double-height and \x1b\x45\x01 for underline
						p.text(center_text("Weighment Slip", 40) + '\n')
						p.text(center_text(f"Weighment Date: {format_date(self.weighment_date)}", 40) + '\n')
						p.text('-' * 40 + '\n')

						lines = [
							f"Entry Type : {self.entry_type}   Branch : {self.branch}",

						]
						if self.supplier_name:
							lines.extend([
								f"Party Name : {self.supplier_name}",
							])

						if self.vehicle_type and self.vehicle_number:
							lines.extend([
								f"Vehicle Type : {self.vehicle_type}   Vehicle No : \x1b\x45\x01{self.vehicle_number}\x1b\x45\x00",
							])

						if self.vehicle_owner == "Third Party":
							lines.extend([
									f"Transporter : \x1b\x45\x01{self.transporter_name}\x1b\x45\x00",
								])
						
						if self.entry_type == "Inward":
							if not self.is_manual_weighment and self.items and (len(self.items) == 1):

								lines.extend([
									f"Item Group : \x1b\x45\x01{self.items[0].get('item_group')}\x1b\x45\x00",
								])
							if not self.is_manual_weighment and self.items and (len(self.items) > 1):

								lines.extend([
									f"Item Name : \x1b\x45\x01Miscellaneous Item\x1b\x45\x00",
								])

							lines.extend([
								f"Inward Date : {format_date(self.inward_date)}   Gross Weight : \x1b\x45\x01{self.gross_weight} K \x1b\x45\x00",
								f"Outward Date : {format_date(self.outward_date)}   Tare Weight : \x1b\x45\x01{self.tare_weight} K \x1b\x45\x00",
							])
						
						if self.entry_type == "Outward":
							if not self.is_manual_weighment and self.item_group:

								lines.extend([
									f"Item Group : {self.item_group}",
								])
							
							lines.extend([
								f"Inward Date : {format_date(self.inward_date)}   Tare Weight : {self.tare_weight} K",
								f"Outward Date : {format_date(self.outward_date)}  Gross Weight : {self.gross_weight} K",
								
							])

						
						

						for line in lines:
							p.text(line + '\n')
						
						p.text('\x1b\x21\x10\x1b\x45\x01' + f"Net Weight : {self.net_weight} K" + '\x1b\x45\x00\x1b\x21\x00' + '\n')  # Double-height and underline

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
						frappe.log_error(frappe.get_traceback(),"Getting second print error for weighment {} ".format(self.reference_record))
					
					finally:
						p.close()
		return True

	@frappe.whitelist()
	def get_first_print(self):
		profile = frappe.get_single("Weighment Profile")
		if profile.enable_printing:
			vid = int(profile.get("vendor_id"), 16)
			pid = int(profile.get("product_id"), 16)
			# vid = f"0x{profile.get('vendor_id')}"
			# pid = f"0x{profile.get('product_id')}"
			if vid and pid:
				try:
					# Initialize the printer
					p = Usb(vid, pid)  # Replace with your printer's vendor and product ID
					p.open()
					

					# ESC/POS commands for formatting
					p.text('\x1b\x45\x01')  # Turn on bold text
					p.text("DATE: {}\n".format(frappe.utils.get_datetime(self.inward_date).strftime("%d-%m-%Y")))
					p.text('\x1b\x45\x00')  # Turn off bold text

					p.text('\x1b\x45\x01')  # Turn on bold text
					p.text("GATE ENTRY: {}\n".format(self.gate_entry_number))
					p.text('\x1b\x45\x00')  # Turn off bold text

					p.text('\x1b\x45\x01')  # Turn on bold text
					# p.text("CARD NUMBER: {}\n\n".format(frappe.db.get_value("Gate Entry", {"name": self.gate_entry_number}, ["card_number"])))
					
						
					p.text("CARD NUMBER: {}\n\n".format(self.get_card_number()))
					p.text('\x1b\x45\x00')  # Turn off bold text

					# Print VEHICLE NO. with larger text size
					p.text('\x1b\x21\x10')  # Select double height mode (adjust as needed)
					p.text("VEHICLE NO.: {}\n".format(self.vehicle_number))
					p.text('\x1b\x21\x00')  # Cancel double height mode

					# Print a line to simulate a border
					p.text('\n' + '-' * 40 + '\n')

					p.cut()

					frappe.msgprint(
						title="Printing...",
						indicator="orange",
						alert=True,
						realtime=True,
						msg="Collect Print"
					)

					
				except Exception as e:
					frappe.log_error(frappe.get_traceback(),"First Print Error against gate entry {}".format(self.gate_entry_number))
				finally:
					p.close()
		return True

	def get_card_number(self):
		card = get_value(doctype="Gate Entry",
				
				docname=self.gate_entry_number,
				fieldname="card_number",
				filters=({"name":self.gate_entry_number})
			)
		return card
	
	@frappe.whitelist()
	def clear_plateform_for_next_weighment(self):
		profile = frappe.get_cached_doc("Weighment Profile")
		if not profile.wake_up_weight:
			frappe.msgprint(
				title="Wakeup Weight Missing for Weigh Bridge",
				msg=f"Please Update Wakeup weight in {get_link_to_form('Weighment Profile','Weighment Profile')}",
			)
		wakeup_weight = profile.wake_up_weight
		while True:
			if read_weigh_bridge()[0] <= wakeup_weight:
				return True
			else:
				
				print("Wating for decreese weight of waybridge...")
				time.sleep(2)
				# return False
	