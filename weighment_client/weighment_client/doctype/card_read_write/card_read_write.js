// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Card Read Write",{


	refresh:function(frm){
		frm.set_value("status","")
		frm.refresh_field()	
		frm.disable_save();

	},

	read: function(frm) {
		frm.set_value("card_number",null)
		frm.refresh_field("card_number")
		frappe.call({
			method: 'read_data',
			doc:frm.doc,
			freeze: true,
            freeze_message: __("Please put the card on Scanning Machine "),
			callback:function(r){
				frm.refresh_fields()
				frappe.show_alert({ message: __("Card read sucessfully"), indicator: "green" });
				// frm.refresh()
			}
		})
	},
	
	generate_new_number:function(frm){
		frappe.call({
			method: 'generate_number',
			doc: frm.doc,
			freeze: true,
            freeze_message: __("Generating card number..."),
			callback:function(r){
				frappe.show_alert({ message: __("Card Number Generated..."), indicator: "green" });
				// frm.reload_doc()
				frm.refresh_fields()
			}
		})
	},

	write:function(frm){
		frappe.call({
			method: 'write_data',
			doc: frm.doc,
			freeze: true,
            freeze_message: __("Updating Data ..."),
			callback:function(r){
				frappe.show_alert({ message: __("Card Number Updated..."), indicator: "green" });
				
				frm.refresh_fields()
				frm.reload_doc()
			}
		})
	},

});
