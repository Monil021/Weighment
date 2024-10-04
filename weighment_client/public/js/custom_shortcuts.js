frappe.ui.keys.add_shortcuts({
    description:"Gate Entry",
    shortcut:"ctrl+alt+g",
    action: () => {
        frappe.set_route("List","Gate Entry")
    }
})