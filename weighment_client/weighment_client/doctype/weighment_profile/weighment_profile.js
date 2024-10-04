// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Weighment Profile", {

    enable_maintanance_mode: function (frm) {
        if (frm.doc.enable_maintanance_mode) {
            if (!frm.doc.weighment_server_url) {
                frm.set_value("enable_maintanance_mode", 0);
                frm.refresh_field("enable_maintanance_mode");
                frappe.throw("Please enter weighment server url first");
            }
            console.log("triggered !!!");
    
            var dialog = new frappe.ui.Dialog({
                title: 'Authentication Required',
                fields: [
                    {
                        fieldname: 'user_id',
                        label: 'User ID',
                        fieldtype: 'Data',
                        reqd: true
                    },
                    {
                        fieldname: 'password',
                        label: 'Password',
                        fieldtype: 'Password',
                        reqd: true
                    }
                ],
                primary_action_label: 'Authenticate',
                primary_action: function () {
                    var data = dialog.get_values();
    
                    // Validate if user_id and password are provided
                    if (!data.user_id || !data.password) {
                        frappe.msgprint(__('Please enter both User ID and Password'));
                        return;
                    }
    
                    frappe.call({
                        method: "authenticate", // Replace with the full path to your method
                        doc: frm.doc,
                        args: {
                            user_id: data.user_id,
                            password: data.password,
                        },
                        callback: function (response) {
                            if (response.message) {
                                let data = response.message;
                                if (data.message == "Logged In") {
                                    frappe.msgprint(__('Authentication Successful'));
                                    frm.doc.authenticated = true; // Set the flag
                                    dialog.hide(); // Close the dialog
                                } else {
                                    frappe.msgprint(__('Authentication Failed: ' + data.message));
                                    frm.set_value('enable_maintanance_mode', 0);
                                    frm.refresh_field('enable_maintanance_mode');
                                }
                            } else {
                                frappe.msgprint(__('Authentication Failed'));
                                frm.set_value('enable_maintanance_mode', 0);
                                frm.refresh_field('enable_maintanance_mode');
                            }
                        }
                    });
                },
                onhide: function () {
                    if (!frm.doc.authenticated) {
                        frm.set_value('enable_maintanance_mode', 0);
                        frm.refresh_field('enable_maintanance_mode');
                    }
                }
            });
            
            dialog.show();
        }
    },
    
    check_bell_switch_status:function(frm) {
        frappe.call({
            method:"weighment_client.weighment_client_utils.check_bell_switch_status",
            args:{
                port:frm.doc.bell_switch_port,
                baud_rate:frm.doc._baud_rate
            },
            freeze: true,
			freeze_message: __("Checking for button press..."),
            callback:function(r) {
                if (r.message) {
                    frappe.show_alert({message:__("Button Press Detected"), indicator:'green'});
                }
                
            }
        })
        
    },
    

    before_load: function(frm) {
        frm.fields_dict['weighbridge_port']._original_value = frm.fields_dict['weighbridge_port'].value;
        frm.fields_dict['bell_switch_port']._original_value = frm.fields_dict['bell_switch_port'].value;
    },

    validate: function(frm) {
        // Counter for is_primary checkboxes
        let primary_count = 0;

        frm.doc.branch_details.forEach(function(row) {
            if (row.is_primary) {
                primary_count++;
            }
        });

        if (primary_count > 1) {
            frappe.msgprint(__('Only one branch can be marked as primary.'));
            frappe.validated = false;
        }
    },
	refresh:function(frm) {
        frm.add_custom_button(__('Get Audio File'), function() {
            fetch_audio_file(frm);
        });

        frappe.call({
			method: "get_locations",
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					frm.fields_dict.location.set_data(r.message)
				}
			}
		});

        if (frm.doc.location){
			frappe.call({
				method: "get_branch_data",
				doc: frm.doc,
				args:{
					location:frm.doc.location
				},
				callback: r => {
					if (r.message) {
						frm.fields_dict.branch_details.grid.update_docfield_property("branch", "options", r.message);
        				frm.refresh_field("branch_details");
					}
				}
			})
		}

        frappe.call({
			method: "get_weighbridge_uom",
			doc: frm.doc,
			callback: function(r) {
				if (r.message) {
					frm.fields_dict.weighbridge_uom.set_data(r.message)
				}
			}
		});
	},

    location:function(frm) {
        if (frm.doc.location){
			frappe.call({
				method: "get_branch_data",
				doc: frm.doc,
				args:{
					location:frm.doc.location
				},
				callback: r => {
					if (r.message) {
						frm.fields_dict.branch_details.grid.update_docfield_property("branch", "options", r.message);
        				frm.refresh_field("branch_details");
					} else {
                        frappe.msgprint("To update branch data please update location into branch on server")
                    }
				}
			})
		}
        
        frm.clear_table("branch_details")
        frm.refresh_field("branch_details")
    },

    update_audio_profiles:function(frm) {
        let audioProfileField = frappe.meta.get_docfield('Audio File Details', 'audio_profile', frm.docname);
        let options = audioProfileField.options.split('\n');

        let existingOptions = frm.doc.audio_file_details.map(row => row.audio_profile);
        options.forEach(option => {
            if (!existingOptions.includes(option)) {
                let newRow = frm.add_child('audio_file_details');
                newRow.audio_profile = option;
            }
        });
        frm.refresh_field('audio_file_details');
    },

    read_port: function(frm){
        frappe.call({
            method: "fetch_port_location",
            doc: frm.doc,
            callback: function(r){
                if (r.message) {
                    let ports = r.message;
                    let options = ports.map(port => ({
                        label: `${port.device} (${port.location})`,
                        value: port.device
                    }));
    
                    let d = new frappe.ui.Dialog({
                        title: __("Select Port"),
                        fields: [
                            {
                                fieldtype: 'Select',
                                fieldname: 'port',
                                label: __('Port'),
                                options: options
                            },
                            {
                                fieldtype: 'Select',
                                fieldname: 'apply_to',
                                label: __('Apply To'),
                                options: [
                                    {label: __('Weighbridge Port'), value: 'weighbridge_port'},
                                    {label: __('Bell Switch Port'), value: 'bell_switch_port'}
                                ]
                            }
                        ],
                        primary_action_label: __('Apply'),
                        primary_action: function(){
                            let selected_port = d.get_value('port');
                            let apply_to = d.get_value('apply_to');
    
                            if (apply_to === 'weighbridge_port') {
                                frm.set_value('weighbridge_port', selected_port);
                            } else if (apply_to === 'bell_switch_port') {
                                frm.set_value('bell_switch_port', selected_port);
                            }
                            
                            d.hide();
                        }
                    });
    
                    d.show();
                } else {
                    frappe.msgprint(__('No ports found.'));
                }
            }
        });
    },

    reset_ports:function(frm) {
        frappe.confirm(
            __('Are you sure you want to reset the ports?'),
            function() {
                // User confirmed to reset
                frm.set_value('weighbridge_port', '');
                frm.set_value('bell_switch_port', '');
                frappe.msgprint(__('Ports have been reset.'));
            },
            function() {
                // User canceled the reset
                frappe.msgprint(__('Ports reset canceled.'));
            }
        );
    },
    
    fetch_ip_address(frm){
        frappe.call({
            method:"fetch_ip_address",
            doc:frm.doc,
            callback(r){
                if(r.message){
                    frm.set_value("system_ip_address",r.message)
                    frm.refresh_field("system_ip_address")
                }
            }
        })
    },

    fetch_admin(frm){
        frappe.call({
            method:"fetch_admin",
            doc:frm.doc,
            callback(r){
                if(r.message){
                    frm.set_value("administrator_user",r.message)
                    frm.refresh_field("administrator_user")
                }
            }
        })
    },
    
    check_password(frm){
        frappe.call({
            method:"get_pass",
            doc:frm.doc,
            callback(r){
                if(r.message){
                    frappe.msgprint(r.message)
                }
            }
        })
    },

    get_string_order(frm){
        frappe.call({
            method:"weighment_client.weighment_client_utils.get_string_order_of_connected_weighbridge",
            callback:function(r){
                if (r.message){
                    frm.set_value("string_order",r.message)
                    frm.refresh_field("string_order")
                }
            }
        })
    },

    fetch_baud_rate:function(frm){
        if (!frm.doc.administrator_password) {
            frappe.throw("Please update System Password on System Settings tab ")
        }
        if (!frm.doc.weighbridge_port) {
            frappe.throw("Please update Weighbridge port first")
        }
        frappe.call({
            method:"weighment_client.weighment_client_utils.fetch_baud_rate",
            freeze: true,
            freeze_message: __("Please Wait..."),
            callback:function(r){
                let baud_rate = r.message.baud_rate;
                let string_order = r.message.alphabet_order;
    
                let d = new frappe.ui.Dialog({
                    title: __("Baud Rate Information"),
                    fields: [
                        { fieldtype: 'Data', fieldname: 'baud_rate', label: __('Baud Rate'), default: baud_rate, read_only: 1 },
                        { fieldtype: 'Data', fieldname: 'string_order', label: __('String Order'), default: string_order, read_only: 1 }
                    ],
                    primary_action_label: __('Apply'),
                    primary_action: function(){
                        frm.set_value('baud_rate', d.get_value('baud_rate'));
                        frm.set_value('string_order', d.get_value('string_order'));
                        d.hide();
                    }
                });
    
                d.show();
            }
        });
    },

    weighbridge_port: function(frm) {
        handle_port_field_change(frm, 'weighbridge_port');
    },

    bell_switch_port: function(frm) {
        handle_port_field_change(frm, 'bell_switch_port');
    },

    update_conversion_table:function(frm){
        frappe.call({
            method:"update_conversion_table",
            doc:frm.doc,
            callback:function(r){
                
                
                frm.refresh_field("weighbridge_uom")
                frm.refresh_field("uom_conversion")
                frm.refresh_field("table_updated")
                frm.dirty();
                
            }
        })
    },
});

function fetch_audio_file(frm) {
    frappe.call({
        method:"fetch_audio_files",
        doc:frm.doc,
        callback:function(r) {
            frm.refresh_field("audio_file_details")
            frm.save()
        }
    });
}

function handle_port_field_change(frm, fieldname) {
    let field_value = frm.fields_dict[fieldname].value;
    if (!field_value) {
        frappe.confirm(
            __("If you remove this content, the port may not work properly. Do you want to continue?"),
            function() {
                // User pressed OK
                frm.fields_dict[fieldname]._original_value = field_value;
            },
            function() {
                // User pressed Cancel
                frm.set_value(fieldname, frm.fields_dict[fieldname]._original_value);
            }
        );
    } else {
        frm.fields_dict[fieldname]._original_value = field_value;
    }
}


frappe.ui.form.on("Branch Table",{
    branch:function(frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        if (child.branch) {
            frappe.run_serially([
                () => frappe.call({
                    method:"get_branch_company",
                    doc:frm.doc,
                    args:{
                        selected_branch:child.branch
                    },
                    callback:function(r){
    
                        if (r.message) {
                            child.company = r.message
                            refresh_field("company",cdn,"branch_details")
                        }
                    }
                }),
                () => frappe.call({
                    method:"get_branch_abbr",
                    doc:frm.doc,
                    args:{
                        selected_branch:child.branch
                    },
                    callback:function(r){
                        if (r.message) {
                            child.abbr = r.message
                            refresh_field("abbr",cdn,"branch_details")
                        }
                    }
                })
            ]);
        } else {
            child.company = null
            refresh_field("company",cdn,"branch_details")
            child.abbr = null
            refresh_field("abbr",cdn,"branch_details")

        }
    },
    
})


// frappe.ui.form.on("Camera Details", {
//     enable: function(frm, cdt, cdn) {
//         const child = locals[cdt][cdn];
//         if (child.enable) {
//             // Set the stream field value based on the number of rows already added
//             var streamValue = "stream" + (frm.doc.__children.length + 1);
//             frappe.model.set_value(cdt, cdn, "stream", streamValue);
//         }
//     }
// });


// function play_audio(frm) {
//     // Get the selected audio profile name
//     const selected_profile = frm.doc.audio_file_details.find(detail => detail.audio_profile === "Please put your card on machine");

//     if (selected_profile) {
//         const file_url = selected_profile.audio_file;

//         if (file_url) {
//             // Create an audio element and play the sound
//             var audio = new Audio(file_url);
//             audio.play();
//         } else {
//             frappe.msgprint(__('Audio file not found.'));
//         }
//     } else {
//         frappe.msgprint(__('Audio profile not found.'));
//     }
// }