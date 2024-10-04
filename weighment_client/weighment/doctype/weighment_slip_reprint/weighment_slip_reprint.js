// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Weighment Slip Reprint", {
	refresh(frm) {
        frm.disable_save()

	},
    get_print: function (frm) {
        frm.call({
            method: "get_print",
            doc:frm.doc,
            callback: function (r) {
                if (r.message) {
                    frappe.show_alert({ message: __("Printing ..."), indicator: 'green' });
                    frm.reload_doc()
                } else {
                    frappe.throw("The weighment ID provided is invalid. Please check the ID and try again.")
                }
            }
        })
    }
});
