import frappe
import requests
from requests.exceptions import RequestException
import json
from frappe.frappeclient import FrappeClient

def check_for_connection():
    try:
        response= requests.get("https://dns.google.com",timeout=5)
        return True
    except requests.ConnectionError:
        return False
        
def insert_document_with_child(doc,do_not_update=None):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        if PROFILE.is_client:
            URL = PROFILE.get("secondary_server_url")
            API_KEY = PROFILE.get("_api_key")
            API_SECRET = PROFILE.get_password("_api_secret")
        else:  
            URL = PROFILE.get("weighment_server_url")
            API_KEY = PROFILE.get("api_key")
            API_SECRET = PROFILE.get_password("api_secret")
        data = doc.as_dict()
        to_remove=['creation','modified',"__unsaved","items","Created By"]
        for d in to_remove:
            if data.get(d):
                data.pop(d)
        # print("Data:----->",data)
        headers = {
            "Authorization": f"token {API_KEY}:{API_SECRET}",
            "Content-Type": "application/json"
        }
        # try:
        items = []
        if doc.items:
            for item in doc.items:
                item_dict = item.as_dict()
                to_remove = ["name", "owner", "creation", "modified", "modified_by", "doctype", "parent", "parenttype", "parentfield","delivery_note_details"]
                for r in to_remove:
                    if item_dict.get(r):
                        item_dict.pop(r)
                items.append(item_dict)
        
            
            data.update({
                "items":items
            })
        
        
        

            
        fields_to_check = ["driver", "transporter","supplier"]
        for field in fields_to_check:
            if data.get(field) and "~" in data.get(field):
                field_value = data.pop(field)
                actual_value = field_value.split("~")[0]
                data[field] = actual_value
        
        # print("type:--->",type(data))
        # print("Data--------->",data)
            
        payload = json.dumps(data,default = str)

        is_document_already_exists = get_value(
            doctype=doc.doctype,
            docname=doc.name,
            fieldname="name"
        )

        if not is_document_already_exists:

            response = requests.post(f"{URL}/api/resource/{doc.doctype}", data=payload, headers=headers)
            # response.raise_for_status()
            if response.status_code == 200:
                frappe.msgprint(
                    title="Recored Created",
                    indicator="orange",
                    alert=True,
                    realtime=True,
                    msg=" Record Created Sucessfully ... ")
            else:
                print("Error:", response.text)
    except RequestException as e:
        frappe.error_log(f"API Document Insert Exception Occurred: {e}")
        print("API Document Insert Exception Occurred:--->", e)



def insert_document(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    data = doc.as_json()
    
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(f"{URL}/api/resource/{doc.doctype}", json=json.loads(data), headers=headers)
        if response.status_code == 200:
            frappe.msgprint(
				title="Recored Created",
				indicator="orange",
				alert=True,
				realtime=True,
				msg=" Record Created Sucessfully ... ")
        else:
            print("Error:", response.text)
    except Exception as e:
        frappe.error_log(f"Exception occurred: {e}")
        print("Exception:", e)


def update_document(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    data = doc.as_dict()
    to_remove=['creation','modified',"__unsaved"]
    for d in to_remove:
        if data.get(d):
            data.pop(d)
    
    params = {}

    payload = json.dumps(data)
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.put(f"{URL}/api/resource/{doc.doctype}/{doc.name}", data=payload,  headers=headers,params=params) #json=json.loads(payload),
        if response.status_code == 200:
            print(response.text)
            # frappe.msgprint("Record updated successfully...")
            frappe.msgprint(
				title="Recored Updated",
				indicator="orange",
				alert=True,
				realtime=True,
				msg=" Record Updated Sucessfully ... ")
    except Exception as e:
        frappe.error_log(f"Exception occurred: {e}")
        print("Exception:", e)

def update_document_with_child(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    data = doc.as_dict()
    to_remove=['creation','modified',"__unsaved","items","Created By","purchase_order_item",]
    for d in to_remove:
        if data.get(d):
            data.pop(d)
    
    fields_to_check = ["driver", "transporter","supplier"]
    for field in fields_to_check:
        if data.get(field) and "~" in data.get(field):
            field_value = data.pop(field)
            actual_value = field_value.split("~")[0]
            data[field] = actual_value
    
    params = {}
    items = []


    
    
    for item in doc.items:
        item_dict = item.as_dict()
        
        to_remove_ = ["name", "owner", "creation", "modified", "modified_by", "doctype", "parent", "parenttype", "parentfield"]
        for r in to_remove_:
            if item_dict.get(r):
                item_dict.pop(r)
        items.append(item_dict)
    data.update({
        "items":items
    })

    po = []
    if doc.purchase_orders:
        for item in doc.purchase_orders:
            item_dict = item.as_dict()
            to_remove = ["name", "owner", "creation", "modified", "modified_by", "doctype", "parent", "parenttype", "parentfield"]
            for r in to_remove:
                if item_dict.get(r):
                    item_dict.pop(r)
            po.append(item_dict)
    
        print("xxxxxxxxxxx",po)
        data.update({
            "purchase_orders":po
        })

    payload = json.dumps(data,default = str)
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.put(f"{URL}/api/resource/{doc.doctype}/{doc.name}", data=payload,  headers=headers,params=params) #json=json.loads(payload),
        print("responce:--->",response.text)
        if response.status_code == 200:
            print(response.text)
            frappe.msgprint(
				title="Recored Updated",
				indicator="orange",
				alert=True,
				realtime=True,
				msg=" Record Updated Sucessfully ... ")
    except Exception as e:
        frappe.error_log(f"Exception occurred: {e}")
        print("Exception:", e)

def update_document_after_submit(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    data = doc.as_dict()
    to_remove=['creation','modified',"__unsaved","amended_from","items","Created By","purchase_orders"]
    for d in to_remove:
        if data.get(d):
            data.pop(d)
    
    fields_to_check = ["driver", "transporter", "supplier"]
    for field in fields_to_check:
        if data.get(field) and "~" in data.get(field):
            field_value = data.pop(field)
            actual_value = field_value.split("~")[0]
            data[field] = actual_value
    
    print("9999999999999",data.get("driver"))
    
    params = {}
    items = []
    if doc.items:
        for item in doc.items:
            item_dict = item.as_dict()
            
            to_remove_ = ["name", "owner", "creation", "modified", "modified_by", "doctype", "parent", "parenttype", "parentfield"]
            for r in to_remove_:
                if item_dict.get(r):
                    item_dict.pop(r)
            items.append(item_dict)
        data.update({
            "items":items
        })


    payload = json.dumps(data,default = str)
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.put(f"{URL}/api/resource/{doc.doctype}/{doc.name}", data=payload,  headers=headers,params=params) #json=json.loads(payload),
        print("responce:--->",response.text)
        if response.status_code == 200:
            print(response.text)
            frappe.msgprint(
				title="Recored Updated",
				indicator="orange",
				alert=True,
				realtime=True,
				msg=" Record Updated Sucessfully ... ")
    except Exception as e:
        frappe.error_log(f"Exception occurred: {e}")
        print("Exception:", e)

def submit_document(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    api = FrappeClient(url=URL,api_key=API_KEY,api_secret=API_SECRET)
    api.submit(doc)
    # data = {
    #     "docname": doc.name,
    #     "doctype": doc.doctype
    # },
    # headers = {
    #     "Authorization": f"token {API_KEY}:{API_SECRET}",
    #     "Content-Type": "application/json"
    # }
    # try:
    #     response = requests.post(f"{URL}/api/method/frappe.client.submit", json=data, headers=headers)
    #     if response.status_code == 200:
    #         frappe.msgprint("Document submitted successfully...")
    #     else:
    #         print("API error:--->",response.text)

    # except Exception as e:
    #     print("error:--->",e)

def cancel_document(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    api = FrappeClient(url=URL,api_key=API_KEY,api_secret=API_SECRET)
    api.cancel(doctype=doc.doctype,name=doc.name)
    # data = {
    #     "docname": doc.name,
    #     "doctype": doc.doctype
    # },
    # headers = {
    #     "Authorization": f"token {API_KEY}:{API_SECRET}",
    #     "Content-Type": "application/json"
    # }
    # try:
    #     response = requests.post(f"{URL}/api/method/frappe.client.cancel/{doc.doctype}/{doc.name}", json=data, headers=headers)
    #     if response.status_code == 200:
    #         frappe.msgprint("Document cancelled successfully...")
    #     else:
    #         print("API error:--->",response.text)

    # except Exception as e:
    #     print("error:--->",e)


def delete_document(doc,do_not_update=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}"
    }
    try:
        response = requests.delete(f"{URL}/api/resource/{doc.doctype}/{doc.name}",headers=headers)
        if response.status_code == 200:
            frappe.msgprint(
				title="Recored Deleted",
				indicator="orange",
				alert=True,
				realtime=True,
				msg=" Record Deleted Sucessfully ... ")
    except Exception as e:
        frappe.error_log(f"Exception occurred: {e}")
        print("Exception:--->", e)


def get_value(docname,fieldname,doctype,filters=None):
    PROFILE = frappe.get_doc("Weighment Profile")
    URL = PROFILE.get("weighment_server_url")
    API_KEY = PROFILE.get("api_key")
    API_SECRET = PROFILE.get_password("api_secret")
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}"
    }
    url = f"{URL}/api/resource/{doctype}/{docname}?fields=[\"{fieldname}\"]"
    if filters:
        url += f"&filters={filters}"
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            data = response.json()
            value = data.get("data", {}).get(fieldname)
            return value
        else:
            print("API error:--->",response.text)
            return None
    except Exception as e:
        print("Exception:--->", e)
        return None
    

def rename_document(doc,new_name):
    PROFILE = frappe.get_doc("Weighment Profile")
    if PROFILE.is_client:
        URL = PROFILE.get("secondary_server_url")
        API_KEY = PROFILE.get("_api_key")
        API_SECRET = PROFILE.get_password("_api_secret")
    else:  
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
    frappe = FrappeClient(api_key=API_KEY,api_secret=API_SECRET,url=URL)
    frappe.rename_doc(doctype=doc.doctype, old_name=doc.name,new_name=new_name)
    

def get_document_names(doctype, fields=["name"], filters=None):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")

        headers = {
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }

        start = 0
        page_length = 200
        
        all_doc_names = []

        while True:
            url = f"{URL}/api/resource/{doctype}?fields={json.dumps(fields)}"
            
            if filters:
                url += f"&filters={json.dumps(filters)}"
            
            url += f"&limit_start={start}&limit_page_length={page_length}"

            response = requests.get(url, headers=headers)
            # response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                doc_names = [doc.get(field) for doc in data["data"] for field in fields]
                all_doc_names.extend(doc_names)
                
                if len(doc_names) < page_length:
                    break
                else:
                    start += page_length
            else:
                frappe.log_error(f"Error getting document names: {response.text}")
                return None
        
        return all_doc_names
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed: Invalid API key or secret.")
        elif e.response.status_code == 403:
            print("Access forbidden: Check your permissions.")
        else:
            print(f"HTTP error occurred: {e}")
        return None


    # except requests.ConnectionError as e:
    #     frappe.log_error(f"Get Document Name Exception occurred:---> {e}")
    #     raise e
    #     return None

def get_child_table_data(docname, child_table_fieldname, doctype):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        headers = {
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        url = f"{URL}/api/resource/{doctype}/{docname}?fields=[\"{child_table_fieldname}\"]"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            child_table_data = data.get("data", {}).get(child_table_fieldname)
            return child_table_data
        else:
            frappe.log_error(f"Error getting child table data: {response.text}")
            return None
    except Exception as e:
        frappe.log_error(f"Exception occurred: {e}")
        return None
    
def get_child_table_data_for_single_doctype(parent_docname, child_table_fieldname):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")

        headers = {
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }

        url = f"{URL}/api/resource/{parent_docname}/{parent_docname}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            child_table_data = data["data"][child_table_fieldname]
            return child_table_data 
        else:
            frappe.log_error(f"Error getting parent document: {response.text}")
            return None
    except Exception as e:
        frappe.log_error(f"Exception occurred: {e}")
        return None
    
def get_combined_document_names(doctype, field_1, field_2, fields=["name"], filters=None):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")

        headers = {
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }

        start = 0
        page_length = 200
        
        combined_names = []

        while True:
            url = f"{URL}/api/resource/{doctype}?fields={json.dumps(fields)}"
            
            if filters:
                url += f"&filters={json.dumps(filters)}"
            
            url += f"&limit_start={start}&limit_page_length={page_length}"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()["data"]
                for doc in data:
                    combined_name = f"{doc[field_1]}~{doc[field_2]}"
                    combined_names.append(combined_name)
                
                if len(data) < page_length:
                    break
                else:
                    start += page_length
            else:
                frappe.log_error(f"Error getting document names: {response.text}")
                return None

        return combined_names
        
    except Exception as e:
        frappe.log_error(f"Error getting document names: {str(e)}")
        return None

@frappe.whitelist()
def get_weighment_mandatory_info(doc):
    doc = doc.as_dict()    
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.get_weighment_mandatory_info"        
        payload = json.dumps({"items": doc.get("items")})
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        
        return response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        frappe.log_error(frappe.get_traceback(), 'Weighment Mandatory Info Error')
        return {"error": str(e)}

@frappe.whitelist()
def get_extra_delivery_stock_settings(doc):
    doc = doc.as_dict()    
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.get_extra_delivery_stock_settings"        
        payload = json.dumps({"items": doc.get("items")})
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        
        return response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        frappe.log_error(frappe.get_traceback(), 'Weighment Mandatory Info Error')
        return {"error": str(e)}



@frappe.whitelist()
def get_purchase_order_items_data(branch,purchase_order,supplier):
    # args = args.as_dict()    
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.get_purchase_order_items_data_from_server"        
        payload = json.dumps({"branch":branch,"supplier":supplier,"purchase_order":purchase_order})
        print("payload:--------->",payload)
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        
        return response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        frappe.log_error(frappe.get_traceback(), 'Purchase Order Item Data Getting Error')
        return {"error": str(e)}




def get_api_data_for_entry_data(doc):
    try:
        doc = doc.as_dict()
        vehicle_types = []
        driver = []
        supplier = []
        vehicle = []
        transporter = []
        item_group = []

        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.get_api_data_for_entry_data"
        payload = json.dumps({"doc": doc})
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        response_data = response.json()
        
        if response.status_code == 200 and "message" in response_data:
            vehicle_types = response_data["message"].get("vehicle_type", [])
            driver = response_data["message"].get("driver", [])
            supplier = response_data["message"].get("supplier", [])
            vehicle = response_data["message"].get("vehicle", [])
            transporter = response_data["message"].get("transporter", [])
            item_group = response_data["message"].get("item_group", [])

        
        return {
            "vehicle_type": vehicle_types, 
            "driver":driver, 
            "supplier":supplier, 
            "vehicle":vehicle, 
            "transporter":transporter, 
            "item_group":item_group
            }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Gate Entry Data Getting Error')
        return {"error": str(e)}

@frappe.whitelist()
def check_item_weight_adjustment_on_weighment(item_code):
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.check_item_weight_adjustment_on_weighment"        
        payload = json.dumps({"item_code":item_code})
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        frappe.log_error(frappe.get_traceback(), 'Weight Adjustment Data Getting Error')
        return {"error": str(e)}
    

@frappe.whitelist()
def get_item_uom(filters):
    item = filters.get("item")
    doc = doc.as_dict()
    try:
        PROFILE = frappe.get_doc("Weighment Profile")
        URL = PROFILE.get("weighment_server_url")
        API_KEY = PROFILE.get("api_key")
        API_SECRET = PROFILE.get_password("api_secret")
        
        path = f"{URL}/api/method/weighment_server.api.update_weighment_before_update_after_submit"        
        payload = json.dumps({"item":item})
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"token {API_KEY}:{API_SECRET}"
        }
        
        response = requests.post(url=path, headers=headers, data=payload)
        print("responce:--------->",response.json())
        
        return response.json()
    except Exception as e:
        print("An error occurred:", str(e))
        frappe.log_error(frappe.get_traceback(), 'Getting Item UOM Info Error')
        return {"error": str(e)}