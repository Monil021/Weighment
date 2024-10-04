# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

import json
import time
import frappe
from frappe.frappeclient import FrappeClient, AuthError, SiteUnreachableError, SiteExpiredError
from frappe.model.document import Document
from frappe.utils.file_manager import save_file
import socket
import os

import requests
import serial
from weighment_client.api import get_allowed_tolerance, get_child_table_data, get_child_table_data_for_single_doctype, get_document_names, get_value
from weighment_client.weighment_client_utils import execute_terminal_commands_for_button_or_weighbridge, get_serial_port, get_system_password, google_voice, play_audio
import serial
from serial.tools import list_ports


class WeighmentProfile(Document):

	@frappe.whitelist()
	def fetch_port_location(self):		
		ports = list(list_ports.comports())
		port_details = [{"device": port.device, "location": port.location} for port in ports]
		return port_details

	@frappe.whitelist()
	def get_locations(self):
		if self.is_enabled:
			location = get_document_names(
				doctype = "Location"
			)
			return location
		
	@frappe.whitelist()
	def get_branch_data(self,location):
		if self.is_enabled:
			branch = get_document_names(
				doctype="Branch",
				filters={"custom_location":location}
			)
			return branch
	
	@frappe.whitelist()
	def get_branch_abbr(self,selected_branch):
		abbr = get_value(
			doctype="Branch",
			docname=selected_branch,
			fieldname="plant_abbr",
			filters=({"name":selected_branch})
		)
		return abbr
	
	@frappe.whitelist()
	def get_branch_company(self,selected_branch):
		company = get_value(
			doctype="Branch",
			docname=selected_branch,
			fieldname="company",
			filters=({"name":selected_branch})
		)		
		return company
	
	@frappe.whitelist()
	def get_weighbridge_uom(self):
		if self.is_enabled:
			uom = get_document_names(
				doctype="UOM",
			)
			return uom

	@frappe.whitelist()
	def fetch_ip_address(self):
		try:
			s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(("8.8.8.8",80))
			ip_address = s.getsockname()[0]
			s.close
			return ip_address
		except Exception as e:
			frappe.throw(
				title="Enexpected Error Found",
				msg= e
			)

	@frappe.whitelist()
	def fetch_admin(self):
		try:
			user = os.getlogin()
			return user
		except Exception as e:
			frappe.throw(
				title="Enexpected Error Found",
				msg=e
			)

	@frappe.whitelist()
	def get_pass(self):
		return self.get_password("administrator_password")
	
	@frappe.whitelist()
	def update_conversion_table(self):
		if self.is_enabled:

			headers = {
				"Authorization": f"token {self.get('api_key')}:{self.get_password('api_secret')}"
			}

			url = f"{self.get('weighment_server_url')}/api/resource/Weighment Client Settings/Weighment Client Settings"
			response = requests.get(url, headers=headers)

			if response.status_code == 200:
				data = response.json()
				if data:
					self.weighbridge_uom = data["data"]["weighbridge_uom"]

			data = get_child_table_data_for_single_doctype(
				parent_docname="Weighment Client Settings",
				child_table_fieldname="uom_conversion"
			)
			if data:
				self.uom_conversion = []
				for d in data:
					self.append("uom_conversion",{
						"uom":d.get("uom"),
						"conversion_factor":d.get("conversion_factor")
					})
					self.table_updated = 1
			
			return True
	
	@frappe.whitelist(allow_guest=True)
	def authenticate(self,user_id, password):
		try:
			login = FrappeClient(url=self.get("weighment_server_url"),username=user_id,password=password)._login(username=user_id,password=password)
			print("login:--->",login)
			return login
		except AuthError:
			return {"message": "Login Unsuccessful"}
		except SiteUnreachableError:
			return {"message": "Site Unreachable"}
		except SiteExpiredError:
			return {"message": "Site Expired"}
		except Exception as e:
			return {"message": str(e)}
		

	@frappe.whitelist()
	def fetch_audio_files(self):		

		api_key = self.get("api_key")
		api_secret = self.get_password("api_secret")

		headers = {
			'Authorization': f'token {api_key}:{api_secret}'
		}

		data = get_child_table_data_for_single_doctype(
			parent_docname="Weighment Client Settings",
			child_table_fieldname="weighment_audio_details"
		)

		if data:
			client_settings_data = data

			for client_audio in client_settings_data:
				client_audio_profile = client_audio.get('audio_profile')
				client_audio_file_url = client_audio.get('audio_file')

				if not client_audio_profile or not client_audio_file_url:
					continue

				download_url = f'{self.weighment_server_url}/api/method/frappe.core.doctype.file.file.download_file?file_url={client_audio_file_url}'
				
				file_response = requests.get(download_url, headers=headers)

				if file_response.status_code == 200:
					file_content = file_response.content
					file_name = client_audio_file_url.split('/')[-1]

					saved_file = save_file(file_name, file_content, 'Weighment Profile', self.name, is_private=1)

					for audio in self.audio_file_details:
						
						if audio.audio_profile == client_audio_profile:
							audio.audio_file = saved_file.file_url
							audio.is_enabled = client_audio.get("is_enabled")

			self.save()

			return {
				'message': 'All files downloaded, saved, and attached to the child table successfully.'
			}
		else:
			return {
				'message': 'No data found in Weighment Audio Settings.'
			}
