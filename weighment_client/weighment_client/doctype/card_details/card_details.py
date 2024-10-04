# Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document

from frappe.frappeclient import FrappeClient
from frappe.utils.data import get_link_to_form
import requests
from frappe import _
from weighment_client.api import get_child_table_data


class CardDetails(Document):
	def after_insert(self):
		PROFILE = frappe.get_doc("Weighment Profile")
		if PROFILE.is_enabled:
			URL = PROFILE.get("weighment_server_url")
			API_KEY = PROFILE.get("api_key")
			API_SECRET = PROFILE.get_password("api_secret")
			path = f"{URL}/api/method/weighment_server.api.create_new_card_details_record"

			payload = {
				"name": self.name,
				"card_number": self.card_number,
				"hex_code": self.hex_code,
				"status": self.status,
				"branch": self.branch,
				"location": self.location,
				"is_assigned": self.is_assigned,
				"is_updated_on_server": self.is_updated_on_server
			}

			headers = {
				"Authorization": f"token {API_KEY}:{API_SECRET}",
				"Content-Type": "application/json"
			}

			try:
				response = requests.post(path, headers=headers, json={"args": payload}, timeout=10)
				response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

				server_response = response.json()
				if server_response.get("isSuccess") == 1:
					self.is_updated_on_server = True
				else:
					frappe.msgprint(server_response.get("message"))

			except requests.exceptions.Timeout:
				frappe.throw(_("Slow internet connection. The request timed out."))
			except requests.exceptions.ConnectionError:
				frappe.throw(_("Please check your network connection."))
			except requests.exceptions.HTTPError as http_err:
				frappe.throw(_("Failed to connect to server. HTTP error occurred: {0}").format(http_err))
			except Exception as err:
				frappe.throw(_("An unexpected error occurred: {0}").format(err))

	
	def on_update(self):
		PROFILE = frappe.get_doc("Weighment Profile")
		if PROFILE.is_enabled:
			URL = PROFILE.get("weighment_server_url")
			API_KEY = PROFILE.get("api_key")
			API_SECRET = PROFILE.get_password("api_secret")

			payload = {
				"name": self.name,
				"card_number": self.card_number,
				"hex_code": self.hex_code,
				"status": self.status,
				"branch": self.branch,
				"location": self.location,
				"is_assigned": self.is_assigned,
				"is_updated_on_server": self.is_updated_on_server
			}

			headers = {
				"Authorization": f"token {API_KEY}:{API_SECRET}",
				"Content-Type": "application/json"
			}

			try:
				response = requests.put(f"{URL}/api/resource/Card Details/{self.name}", json=payload, headers=headers, timeout=10)
				response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

				if response.status_code != 200:

					server_response = response.json()
					frappe.msgprint(_("Server response: {0}").format(server_response.get('message', 'No message')))

			except requests.exceptions.Timeout:
				frappe.msgprint(_("Slow internet connection. The request timed out."))
			except requests.exceptions.ConnectionError:
				frappe.msgprint(_("Please check your network connection."))
			except requests.exceptions.HTTPError as http_err:
				if response.status_code == 404:
					frappe.msgprint(_("Resource not found. Please check if the Card Details resource with name '{0}' exists on the server.").format(self.name))
			except Exception as err:
				frappe.msgprint(_("An unexpected error occurred: {0}").format(err))


	def on_trash(self):
		PROFILE = frappe.get_doc("Weighment Profile")
		if not PROFILE.enable_maintanance_mode:
			frappe.throw("Not allowed to perform this action, Maintanance mode disabled on {}".format(get_link_to_form("Weighment Profile","Weighment Profile")))
		if PROFILE.is_enabled:
			URL = PROFILE.get("weighment_server_url")
			API_KEY = PROFILE.get("api_key")
			API_SECRET = PROFILE.get_password("api_secret")
			headers = {
				"Authorization": f"token {API_KEY}:{API_SECRET}"
			}
			try:
				response = requests.delete(f"{URL}/api/resource/Card Details/{self.name}",headers=headers)
				if response.status_code == 200:
					frappe.msgprint("Record Deleted Sucessfully")
			except Exception as e:
				frappe.error_log(f"Exception occurred: {e}")
				print("Exception:", e)

