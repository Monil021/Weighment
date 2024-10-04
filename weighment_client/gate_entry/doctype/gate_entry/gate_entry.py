# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
import requests
from weighment_client.api import check_item_weight_adjustment_on_weighment, get_api_data_for_entry_data, get_document_names, get_extra_delivery_stock_settings, get_purchase_order_items_data, get_stock_entry_item_data, get_subcontracting_order_items_data, get_value, get_weighment_mandatory_info, validate_gate_entry_velicle
from weighment_client.weighment_client_utils import read_smartcard

class OverAllowanceError(frappe.ValidationError):
	pass


class GateEntry(Document):

	def onload(self):
		self.location = frappe.db.get_single_value("Weighment Profile","location")
		self.url = frappe.db.get_single_value("Weighment Profile","system_ip_address")
	
	@frappe.whitelist()
	def get_gate_entry_data(self):
		return get_api_data_for_entry_data(self)
	
	@frappe.whitelist()
	def get_branches(self):
		return [k.branch for k in frappe.get_all("Branch Table",["branch"])]
		
	@frappe.whitelist()
	def get_company(self):
		return frappe.db.get_value("Branch Table",{"branch":self.branch},["company"])

	@frappe.whitelist()
	def get_branch_abbr(self):
		return frappe.db.get_value("Branch Table",{"branch":self.branch},["abbr"])

	@frappe.whitelist()
	def check_weighment_required_details(self,selected_item_group):
		if selected_item_group and "~" in selected_item_group:
			selected_item_group = selected_item_group.split("~")[0]
		
		print("item_group",selected_item_group)
		value = get_value(
			docname=selected_item_group,
			fieldname="custom_is_weighment_required",
			doctype="Item Group",
			filters=({"name":selected_item_group})
		)
		if value == "Yes":
			self.is_weighment_required = "Yes"
		else:
			self.is_weighment_required = "No"
		return True
	
	@frappe.whitelist()
	def get_subcontracting_orders(self,selected_supplier):
		return get_document_names(
			doctype="Subcontracting Order",
			filters={"docstatus":1,"branch":self.branch,"supplier":selected_supplier},
		)
	
	@frappe.whitelist()
	def get_purchase_orders(self,selected_supplier):
		po = get_document_names(
			doctype="Purchase Order",
			filters={"docstatus":1,"branch":self.branch,"supplier":selected_supplier,"per_received":["<",100]},
		)
		if po and not self.purchase_orders:
			for d in po:
				self.append("purchase_orders",{
					"purchase_orders":d
				})
		return po
	
	@frappe.whitelist()
	def fetch_po_item_details(self):
		items = []
		if self.purchase_orders:
			for d in self.purchase_orders:
				data = get_purchase_order_items_data(branch=self.branch,supplier=self.supplier.split("~")[0],purchase_order=d.purchase_orders)
				if data and "message" in data:
					items.extend(data["message"])

		self.items = []
		for d in items:
			self.append("items",{
				"item_code":d.get("item_code"),
				"item_name":d.get("item_name"),
				"qty":d.get("qty"),
				"description":d.get("description"),
				"gst_hsn_code":d.get("gst_hsn_code"),
				"item_code":d.get("item_code"),
				"brand":d.get("brand"),
				"is_ineligible_for_itc":d.get("is_ineligible_for_itc"),
				"stock_uom":d.get("stock_uom"),
				"uom":d.get("uom"),
				"conversion_factor":d.get("conversion_factor"),
				"stock_qty":d.get("stock_qty"),
				"actual_received_qty":d.get("received_qty"),
				"rate":d.get("rate"),
				"amount":d.get("amount"),
				"item_tax_template":d.get("item_tax_template"),
				"gst_treatment":d.get("gst_treatment"),
				"rate_company_currency":d.get("base_rate"),
				"amount_company_currency":d.get("base_amount"),
				"weight_per_unit":d.get("weight_per_unit"),
				"weight_uom":d.get("weight_uom"),
				"total_weight":d.get("total_weight"),
				"warehouse":d.get("warehouse"),
				"material_request":d.get("material_request"),
				"material_request_item":d.get("material_request_item"),
				"delivery_note_item":d.get("delivery_note_item"),
				"purchase_order":d.get("parent"),
				"purchase_order_item":d.get("name"),
				"expense_account":d.get("expense_account"),
				"branch":d.get("branch"),
				"cost_center":d.get("cost_center"),
			})
	
	@frappe.whitelist()
	def get_stock_entrys(self,selected_supplier):
		se = get_document_names(
			doctype="Stock Entry",
			filters={
				"docstatus":1,
				"company":self.company,
				"supplier":selected_supplier,
				"stock_entry_type":"Send to Subcontractor",
				"custom_job_work_challan":1,
				"add_to_transit":1
				},
		)
		if se and not self.stock_entrys:
			for d in se:
				self.append("stock_entrys",{
					"stock_entry":d
				})
		return se
	
	@frappe.whitelist()
	def fetch_so_item_details(self):
		items = []
		if self.subcontracting_orders:
			for d in self.subcontracting_orders:
				data = get_subcontracting_order_items_data(branch=self.branch,supplier=self.supplier.split("~")[0],subcontracting_order=d.subcontracting_order)
				if data and "message" in data:
					items.extend(data["message"])


		self.subcontracting_details = []
		if items:
			for d in items:
				self.append("subcontracting_details",{
					"item_code":d.get("item_code"),
					"item_name":d.get("item_name"),
					"qty":d.get("qty"),
					"description":d.get("description"),
					"stock_uom":d.get("stock_uom"),
					"conversion_factor":d.get("conversion_factor"),
					"rate":d.get("rate"),
					"amount":d.get("amount"),
					"warehouse":d.get("warehouse"),
					"material_request":d.get("material_request"),
					"material_request_item":d.get("material_request_item"),
					"subcontracting_order":d.get("parent"),
					"purchase_order_item":d.get("name"),
					"expense_account":d.get("expense_account"),
					"branch":d.get("branch"),
					"cost_center":d.get("cost_center"),
				})

	@frappe.whitelist()
	def fetch_stock_entry_item_data(self):
		if not self.stock_entrys:
			frappe.throw("Please select stock entry first")

		items = []
		if self.stock_entrys:
			for d in self.stock_entrys:
				data = get_stock_entry_item_data(
					company=self.company,
					supplier=self.supplier.split("~")[0],
					stock_entry=d.stock_entry
				)
				if data and "message" in data:
					items.extend(data["message"])
					

		self.stock_entry_details = []
		if items:
			for j in items:
				self.append("stock_entry_details",{
					"item_code":j.get("item_code"),
					"item_name":j.get("item_name"),
					"qty":j.get("qty"),
					"item_group":j.get("item_group")
				})
	
	@frappe.whitelist()
	def validate_purchase_entry(self):
		item_groups = {}
		weighable_entry = {}
			
		if self.entry_type == "Inward" and not self.items and not self.is_manual_weighment and not self.is_subcontracting_order and not self.job_work:
			frappe.throw("Fetch Items Data First")
		
		if self.entry_type == "Inward" and not self.subcontracting_details and not self.is_manual_weighment and self.is_subcontracting_order and not self.job_work:
			frappe.throw("Fetch Subcontracting Item Data First")
		
		if self.entry_type == "Inward" and self.items and not self.is_manual_weighment and not self.job_work and not self.is_subcontracting_order:
			a_data = get_weighment_mandatory_info(self)["message"]
			weighment_mandatory_status = None
			ig = None
			for l in a_data:
				for k in self.items:
					if l.get("item_code") == k.get("item_code"):
						current_weighment_status = l.get("custom_is_weighment_mandatory")
						item_group = l.get("ig")
					
						if weighment_mandatory_status is None:
							weighment_mandatory_status = current_weighment_status
						elif weighment_mandatory_status != current_weighment_status:
							frappe.msgprint(
								title="Multiple Found", 
								msg=f"Item {k.get('item_code')} you are trying to add has different weighment statuses."
							)
						if weighable_entry.get(l.get("custom_is_weighment_mandatory")):
							if weighable_entry[l.get("item_code")] and weighable_entry[l.get("item_code")][l.get("custom_is_weighment_mandatory")] != l.get("custom_is_weighment_mandatory"):
								frappe.msgprint(
									title="Multiple Found", 
									msg=f"Item {k.get('item_code')} you are trying to add has different items where some of items are not weighable"
								)
						if ig is None:
							ig = item_group
						elif ig != item_group:
							frappe.msgprint(
								title="Multiple Found", 
								msg=f"Item {k.get('item_code')} you are trying to add has different Item group apart from others items."
							)
						if k.item_code and l.get("custom_is_weighment_mandatory") == "Yes":
							k.is_weighable_item = 1
							self.is_weighment_required = "Yes"
						else:
							k.is_weighable_item = 0
							self.is_weighment_required = "No"
		return True
	
	@frappe.whitelist()
	def validate_extra_delivery_details(self):
		if self.entry_type == "Inward" and not self.is_manual_weighment and not self.job_work and not self.is_subcontracting_order:
			action_msg = frappe._(
				'To allow over receipt / delivery, update "Over Receipt/Delivery Allowance" in Stock Settings or the Item.'
			)
			data = get_extra_delivery_stock_settings(self)["message"]
			
			if data:
				for d in self.items:
					for l in data:
						if d.get("item_code") == l.get("item_code"):
							allowed_extra_percentage = l.get("odr_per")
							if allowed_extra_percentage:
								allowed_qty = d.get("qty") + d.get("actual_received_qty") + (d.get("qty") * allowed_extra_percentage / 100)

								if allowed_extra_percentage and ((d.accepted_quantity + d.rejected_quantity + d.actual_received_qty) > allowed_qty):
									over_limit_qty = (d.accepted_quantity + d.rejected_quantity + d.actual_received_qty) - allowed_qty
									frappe.throw(
										frappe._(
											"This document is over limit by {0} {1} for item {2}. Are you making another {3} against the same {4}?"
										).format(
											frappe.bold(_("Qty")),
											frappe.bold(over_limit_qty),
											frappe.bold(d.get("item_code")),
											frappe.bold(_("Purchase Receipt")),
											frappe.bold(_("Gate Entry")),
										)
										+ "<br><br>"
										+ action_msg,
										OverAllowanceError,
										title=_("Limit Crossed"),
									)

			if not data:
				for d in self.items:
					accepted_qty = 0
					rejected_qty = 0
					actual_received_qty = 0
					accepted_qty = d.accepted_quantity if d.accepted_quantity else 0
					rejected_qty = d.rejected_quantity if d.rejected_quantity else 0
					actual_received_qty = d.actual_received_qty if d.actual_received_qty else 0
					if (accepted_qty + rejected_qty + actual_received_qty) > d.qty:
						over_limit_qty = (accepted_qty + rejected_qty + actual_received_qty) - d.qty
						frappe.throw(
							frappe._(
								"This document is over limit by {0} {1} for item {2}. Are you making another {3} against the same {4}?"
								).format(
									frappe.bold(_("Qty")),
									frappe.bold(over_limit_qty),
									frappe.bold(d.get("item_code")),
									frappe.bold(_("Purchase Receipt")),
									frappe.bold(_("Gate Entry")),
								)
								+ "<br><br>"
								+ action_msg,
								OverAllowanceError,
								title=_("Limit Crossed"),
						)
						
		if self.entry_type == "Outward" and not self.is_manual_weighment and not self.job_work and not self.is_subcontracting_order:
			self.check_weighment_required_details(selected_item_group=self.item_group)

		# if self.job_work:
		# 	if not self.stock_entry_details:
		# 		frappe.throw("Fetch stock entry data first")

		# 	self.is_weighment_required = "Yes" if self.job_work_weighment_required == "Yes" else "No"
		# 	print("weighment required:--->",self.is_weighment_required,self.job_work_weighment_required)
			
		if self.entry_type == "Inward" and self.items and not self.is_manual_weighment and not self.is_subcontracting_order and not self.job_work:
			for d in self.items:
				item = d.get("item_code")
				enable_weight_adjustment = check_item_weight_adjustment_on_weighment(item_code=item)
				if enable_weight_adjustment and "message" in enable_weight_adjustment:
					enable_weight_adjustment = enable_weight_adjustment["message"]
					if enable_weight_adjustment:
						self.enable_weight_adjustment = 1
			if self.enable_weight_adjustment and len(self.items) >= 2:
				frappe.throw(f"Not allow to add more than two items")
		
		self.validate_vehicle()
		return True
	

	def validate_vehicle(self):
		if self.is_weighment_required == "Yes":
			data = validate_gate_entry_velicle(doc=self)
			if data and "message" in data:
				data = data["message"]
				if data:
					weighment_server_url = frappe.get_single('Weighment Profile').get_value('weighment_server_url')
					
					message = (f"Entered Vehicle Number {self.vehicle_number} is already exist in Gate Entry "
						f"{data} on "
						f"<a href='{weighment_server_url}'>{weighment_server_url}</a> which is not completed yet")
					frappe.throw(message)

	def validate_card(self):
		if self.read_card():

			card_number = self.read_card()
			is_assigned = get_value(
				docname=card_number,
				doctype="Card Details",
				filters=({"card_number":card_number}),
				fieldname="is_assigned"
			)
			
			if is_assigned == 1:
				frappe.throw("This card is already assigned to other")


	@frappe.whitelist()
	def read_card(self):
		data = read_smartcard()
		get_card_number = frappe.db.get_value("Card Details", {"hex_code": data}, ["card_number"])
		if get_card_number:
			return get_card_number
		else:
			frappe.throw("No data found on the card.")

	@frappe.whitelist()
	def validate_card_data(self):
		if not self.read_card():
			frappe.throw("No data found from this card")
		if not self.validate_card():
			self.card_number = self.read_card()
		
		return True

	@frappe.whitelist()
	def create_gate_entry(self):
		try:
			profile = frappe.get_single("Weighment Profile")

			path = f"{profile.get('weighment_server_url')}/api/method/weighment_server.api.create_gate_entry"
			data = self.as_dict()

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
			'''getting responce like :---> {"message":{"status":"success","gate_entry_name":"GE-RDPLK-24-000008"}}'''

			response = response.json()

			print("************",response["message"])
			
			if response and "message" in response:
				response = response["message"]
				print("response:----->",response[0])
				return response
			
			else:
				frappe.throw(frappe.get_traceback())

			
		except:
			frappe.throw(frappe.get_traceback())
		