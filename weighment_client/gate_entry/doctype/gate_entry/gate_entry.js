// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Entry", {
	refresh(frm) {
        frm.disable_save()
        frm.trigger("make_custom_buttons")
        frm.trigger("get_onload_data")
	},

    make_custom_buttons: function(frm) {
        
        frm.add_custom_button(__("Save"), function() {
            frappe.run_serially([
                () => frm.trigger("validate_driver_contact"),
                
                () => frm.trigger("before_save_validations"),
    
                () => frm.trigger("validate_purchase_entry").then((valid) => {
                    if (!valid) {
                        frappe.throw(__("Purchase entry validation failed"));
                        return false;
                    }
                }),
    
                () => frm.trigger("validate_extra_delivery_details").then((valid) => {
                    if (!valid) {
                        frappe.throw(__("Extra delivery details validation failed"));
                        return false;
                    }
                }),
    
                () => frm.trigger("validate_card").then((valid) => {
                    if (!valid) {
                        frappe.throw(__("Card validation failed"));
                        return false;
                    }
                }),
    
                () => frm.trigger("create_gate_entry")
            ]);
        })
    },
	create_gate_entry: function(frm) {
		let message = `
			<div>
				<p>
					<b>Warning: This Action Cannot Be Undone!</b>
				</p>
				<p>
					You are about to create a Gate Entry, which is a critical step in the process.
				</p>
				<p>
					<b>Please ensure that all values you have entered are correct, including the vehicle details, driver information, and the weight/quantity received.</b>
				</p>
				<p>Are you sure you want to proceed with creating the Gate Entry?</p>
			</div>`;
	
		frappe.confirm(
			__(message),
			function() {
				frm.call({
					method: "create_gate_entry",
					doc: frm.doc,
					freeze: true,
					freeze_message: __("Creating Gate Entry..."),
					callback: function(r) {
						console.log("Gate entry created successfully:", r.message);
	
						// Check if the response contains the 'status' and 'gate_entry_name'
						if (r.message && r.message[0] === "success") {
							frappe.show_alert({
								message: __( `Gate Entry Created: ${r.message[1]}` ),
								indicator: 'green'
							});
							frm.reload_doc();
						} else {
							frappe.msgprint(__("Gate Entry creation failed. Please try again."));
						}
					},
					error: function(err) {
						console.error("Error during gate entry creation", err);
					}
				});
			},
			function() {
				console.log("Gate entry creation canceled");
			}
		);
	},
	

    // create_gate_entry: function(frm) {
    //     let message = `
    //         <div>
    //             <p>
    //                 <b>Warning: This Action Cannot Be Undone!</b>
    //             </p>
    //             <p>
    //                 You are about to create a Gate Entry, which is a critical step in the process.
    //             </p>
    //             <p>
    //                 <b>Please ensure that all values you have entered are correct, including the vehicle details, driver information, and the weight/quantity received.</b>
    //             </p>
    //             <p>Are you sure you want to proceed with creating the Gate Entry?</p>
    //         </div>`;
    
    //     frappe.confirm(
    //         __(message),
    //         function() {
    //             frm.call({
    //                 method: "create_gate_entry",
    //                 doc: frm.doc,
    //                 freeze: true,
    //                 freeze_message: __("Creating Gate Entry..."),
    //                 callback: function(r) {
    //                     console.log("Gate entry created successfully:", r.message);
	// 					if (r.message && "message" in r.message) {
	// 						var msg = r.message.message
	// 						if (msg.status === "success") {
	// 							frappe.show_alert({message:__(`Gate Entry Created: ${msg.gate_entry_name}`), indicator:'green'});
	// 						}
	// 					}
    //                 }
    //             });
    //         },
    //         function() {
    //             console.log("Gate entry creation canceled");
    //         }
    //     );
    // },
    

    before_save_validations: function (frm) {
        return new Promise((resolve, reject) => {
            if (!frm.doc.vehicle_type) {
                frappe.throw("Please Select Vehicle Type First");
                reject(false);
                return;
            }
    
            if (!frm.doc.driver_name) {
                frappe.throw("Please Select Driver Name First");
                reject(false);
                return;
            }
    
            if (!frm.doc.driver_contact) {
                frappe.throw("Please Enter Driver Contact First");
                reject(false);
                return;
            }
    
            if (frm.doc.vehicle_owner === "Company Owned" && !frm.doc.vehicle) {
                frappe.throw("Please Select Vehicle First");
                reject(false);
                return;
            }
    
            if (frm.doc.vehicle_owner === "Third Party" && !frm.doc.vehicle_number) {
                frappe.throw("Please Enter Vehicle Number");
                reject(false);
                return;
            }
    
            frm.doc.items.forEach(element => {
                if (element.received_quantity <= 0) {
                    frappe.throw(`Received Quantity can't be zero at row ${element.idx}`);
                    reject(false);
                    return;
                }
            });
    
            resolve(true);
        });
    },
    

    validate_extra_delivery_details: function (frm) {
        return new Promise((resolve, reject) => {
            frm.call({
                method: "validate_extra_delivery_details",
                doc: frm.doc,
                callback: function (r) {
                    console.log("log from validate extra delivery:----->", r.message);
                    if (r.message) {
                        frm.refresh_field("is_weighment_required");
                        resolve(true);
                    } else {
                        resolve(false);
                    }
                },
                error: function(err) {
                    console.error("Validation error", err);
                    reject(err);
                }
            });
        });
    },

    validate_purchase_entry: function(frm) {
        return new Promise((resolve, reject) => {
            frm.call({
                method: "validate_purchase_entry",
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        frm.refresh_field("is_weighment_required");
                        resolve(true);
                    } else {
                        reject(false);
                    }
                },
                error: function(err) {
                    console.error("Error during purchase entry validation", err);
                    reject(err);
                }
            });
        });
    },
    

    validate_card: function(frm) {
        return new Promise((resolve, reject) => {
            if (!frm.doc.card_number && frm.doc.is_weighment_required === "Yes" && 
                (frm.doc.is_weighment_required === "Yes" || (frm.doc.is_manual_weighment && !frm.doc.job_work))) {
                
                frm.call({
                    method: "validate_card_data",
                    doc: frm.doc,
                    freeze: true,
                    freeze_message: __("Please put the card on card reader..."),
                    callback: function(r) {
                        if (r.message) {
                            frm.refresh_field("card_number");
                            resolve(true);
                        } else {
                            reject(false);
                        }
                    },
                    error: function(err) {
                        console.error("Error during card validation", err);
                        reject(err);
                    }
                });
            } else {
                resolve(true);
            }
        });
    },
    

    get_onload_data: function (frm) {

        frappe.call({
			method:"get_branches",
			doc:frm.doc,
			callback:function(r) {
				if (r.message) {
					frm.fields_dict.branch.set_data(r.message);
					frm.refresh_field("branch")
				}
			}
		})

        frappe.call({
			method:"get_gate_entry_data",
			doc:frm.doc,
			freeze: true,
			freeze_message: __("Getting Data Via Api..."),
			callback:function(r) {
				var vehicle_type = r.message.vehicle_type
				var driver = r.message.driver
				var supplier = r.message.supplier
				var vehicle = r.message.vehicle
				var transporter = r.message.transporter
				var item_group = r.message.item_group
				if (vehicle_type) {
					frm.fields_dict.vehicle_type.set_data(vehicle_type)
					frm.refresh_field("vehicle_type")	
				}
				if (driver) {
					frm.fields_dict.driver.set_data(driver)
					frm.refresh_field("driver")
				}
				if (supplier) {
					frm.fields_dict.supplier.set_data(supplier)
					frm.refresh_field("supplier")
				}
				if (vehicle) {
					frm.fields_dict.vehicle.set_data(vehicle)
					frm.refresh_field("vehicle")
				}
				if (transporter) {
					frm.fields_dict.transporter.set_data(transporter)
					frm.refresh_field("transporter")
				}
				if (item_group) {
					frm.fields_dict.item_group.set_data(item_group)
					frm.refresh_field("item_group")
				}
			}
		})
    },

    branch:function(frm) {
		if (frm.doc.branch) {
			frappe.run_serially([
				() => frappe.call({
					method:"get_company",
					doc:frm.doc,
					callback:function(r) {
						if (r.message) {
							frm.set_value("company",r.message)
							frm.refresh_field("company")
						}
					}
				}),

				() => frappe.call({
					method:"get_branch_abbr",
					doc:frm.doc,
					callback:function(r) {
						if (r.message) {
							frm.set_value("abbr",r.message)
							frm.refresh_field("abbr")
						}
					}
				}),

			])
		} else {
			frm.set_value("company",null)
			frm.set_value("abbr",null)
			frm.refresh_field("company")
			frm.refresh_field("abbr")
		}
		frm.set_value("supplier",null)
		frm.refresh_field("supplier")
	},

    is_manual_weighment:function(frm) {
		if (frm.doc.is_weighment_required) {
			frm.clear_table("purchase_orders")
			frm.clear_table("items")
			frm.refresh_field("purchase_orders"),
			frm.refresh_field("items")
		}
	},

    job_work:function(frm) {
		if (frm.doc.job_work) {
			frm.set_value("is_manual_weighment",1)
			frm.set_df_property("is_manual_weighment","read_only",true)
			frm.clear_table("purchase_orders")
			frm.clear_table("items")
			frm.refresh_field("purchase_orders"),
			frm.refresh_field("items")
		} else {
			frm.set_value("is_manual_weighment",0)
			frm.set_df_property("is_manual_weighment","read_only",false)
			frm.clear_table("stock_entrys")
			frm.clear_table("stock_entry_details")
			frm.set_value("supplier",null)
			frm.refresh_field("stock_entry")
			frm.refresh_field("supplier")
			frm.refresh_field("stock_entry_details")
		}
		frm.set_value("supplier",null)
		frm.refresh_field("supplier")
	},

    entry_type: function (frm) {
        frm.set_value("supplier",null)
        frm.set_value("supplier_name",null)
        frm.clear_table("purchase_orders")
        frm.refresh_field("purchase_orders")

    },

    vehicle_owner: function (frm) {
        frm.set_value("driver",null)
        frm.set_value("driver_name",null)
        frm.set_value("driver_contact",null)
    },

    driver:function(frm) {
		if (frm.doc.driver) {
			frm.set_value("driver_name",frm.doc.driver.split("~")[1])
			frm.refresh_field("driver_name")
		} else {
			frm.set_value("driver_name",null)
			frm.refresh_field("driver_name")
		}
	},

    item_group:function(frm) {
		if (frm.doc.entry_type === "Outward") {
			frm.events.checkWeighmentRequired(frm);
		}
	},

	checkWeighmentRequired:function(frm){
		if (frm.doc.item_group) {
			frappe.call({
				method:"check_weighment_required_details",
				doc:frm.doc,
				freeze:true,
				args:{
					selected_item_group:frm.doc.item_group
				},
				callback: r => {
					if (r.message) {
						frm.refresh_field("is_weighment_required")
					}
				}
			})
		}
	},

    vehicle:function(frm){
		if (frm.doc.vehicle_owner === "Company Owned") {
			frm.set_value("vehicle_number",frm.doc.vehicle)
			frm.refresh_field("vehicle_number")
		} 
		else {
			frm.set_value("vehicle_number",null)
			frm.refresh_field("vehicle_number")
		}
	},

    transporter:function(frm) {
		if (frm.doc.transporter) {
			frm.set_value("transporter_name",frm.doc.transporter.split("~")[1])
			frm.refresh_field("transporter_name")
		} else {
			frm.set_value("transporter_name",null)
			frm.refresh_field("transporter_name")
		}
	},

    supplier:function(frm) {

		if (frm.doc.supplier && !frm.doc.branch) {
			frm.set_value("supplier",null)
			frm.refresh_field("supplier")
			frappe.msgprint("Please Select The Branch First")
		}

		if (frm.doc.supplier) {
			frm.set_value("supplier_name",frm.doc.supplier.split("~")[1])
			frm.refresh_field("supplier_name")
		} else {
			frm.set_value("supplier_name",null)
			frm.refresh_field("supplier_name")
		}

		if (frm.doc.docstatus != 1 && frm.doc.supplier && frm.doc.branch){
			if (frm.doc.is_subcontracting_order) {
				frappe.call({
					method: "get_subcontracting_orders",
					doc: frm.doc,
					args:{
						selected_supplier:frm.doc.supplier.split("~")[0]
					},
					callback: r => {
						if (r.message) {
							frm.fields_dict.subcontracting_orders.grid.update_docfield_property("subcontracting_order", "options", r.message);
							frm.refresh_field("subcontracting_orders");
						}
					}
				})
			} else if (!frm.doc.job_work) {
				frappe.call({
					method: "get_purchase_orders",
					doc: frm.doc,
					args:{
						selected_supplier:frm.doc.supplier.split("~")[0]
					},
					callback: r => {
						if (r.message) {

							frm.fields_dict.purchase_orders.grid.update_docfield_property("purchase_orders", "options", r.message);
							frm.refresh_field("purchase_orders");
							frm.refresh_field("purchase_orders");
						}
					}
				})
			} else if (frm.doc.job_work) {
				frappe.call({
					method: "get_stock_entrys",
					doc: frm.doc,
					args:{
						selected_supplier:frm.doc.supplier.split("~")[0]
					},
					callback: r => {
						if (r.message) {
							console.log("*****************",r.message)
							frm.fields_dict.stock_entrys.grid.update_docfield_property("stock_entry", "options", r.message);
							frm.refresh_field("stock_entrys");
						}
					}
				})
			}
		}
		frm.clear_table("purchase_orders")
		frm.refresh_field("purchase_orders")
		frm.clear_table("subcontracting_orders")
		frm.refresh_field("subcontracting_orders")
		frm.clear_table("subcontracting_details")
		frm.refresh_field("subcontracting_details")
		frm.clear_table("items")
		frm.refresh_field("items")
		frm.clear_table("stock_entrys")
		frm.refresh_field("stock_entrys")
		frm.clear_table("stock_entry_details")
		frm.refresh_field("stock_entry_details")
	},

    validate_driver_contact: function(frm) {
        return new Promise((resolve, reject) => {
            const phone_regex = /^\d{10}$/;
            
            if (!phone_regex.test(frm.doc.driver_contact)) {
                frappe.throw(__('Please enter a valid 10-digit phone number'));
                reject(false);
            } else {
                resolve(true);
            }
        });
    },
    

    is_weighment_required:function(frm){
		if (frm.doc.is_weighment_required === "No" && frm.doc.card_number) {
			frm.set_value("card_number","")
			frm.refresh_field("card_number")
		}
	},

    fetch_purchase_details:function(frm){
		frappe.call({
			method:"fetch_po_item_details",
			doc:frm.doc,
			freeze: true,
            freeze_message: __("Getting Items Data..."),
			callback:function(r){
				frm.refresh_field("items")
			}
		})
	},

    fetch_subcontracting_details:function(frm){
		frappe.call({
			method:"fetch_so_item_details",
			doc:frm.doc,
			freeze: true,
            freeze_message: __("Getting Subcontracting Order Data..."),
			callback:function(r){
				frm.refresh_field("subcontracting_details")
			}
		})
	},

    fetch_stock_entry_details:function(frm) {
		frappe.call({
			method:"fetch_stock_entry_item_data",
			doc:frm.doc,
			freeze: true,
            freeze_message: __("Getting Stock Entry Details Data..."),
			callback:function(r){
				frm.refresh_field("stock_entry_details")
			}
		})
	},
  
});

frappe.ui.form.on("Stock Entrys", {
    stock_entry: function(frm, cdt, cdn) {
        const child = locals[cdt][cdn];

        var existing_data = [];
        frm.doc.stock_entrys.forEach(element => {
            if (element.stock_entry && element.name !== child.name) {
                existing_data.push(element.stock_entry);
            }
        });

        if (existing_data.includes(child.stock_entry)) {
			frappe.model.set_value(cdt, cdn, "stock_entry", "");
            frappe.throw("This stock entry already exists.");
            
        } 

		frm.clear_table("stock_entry_details")
		frm.refresh_field("stock_entry_details")
    },
	
	accepted_quantity:function(frm,cdt,cdn) {
		const child = locals[cdt][cdn];
		console.log("$$$$$$$$$$$$$$")
		child.received_quantity = child.accepted_quantity + child.rejected_quantity
		refresh_field("received_quantity",cdn,"items")
	}
	
});

frappe.ui.form.on("Purchase Orders", {
    purchase_orders: function(frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        console.log("selected po:--->", child.purchase_orders);

        var existing_data = [];
        frm.doc.purchase_orders.forEach(element => {
            if (element.purchase_orders && element.name !== child.name) {
                existing_data.push(element.purchase_orders);
            }
        });

        if (existing_data.includes(child.purchase_orders)) {
			frappe.model.set_value(cdt, cdn, "purchase_orders", "");
            frappe.throw("This purchase order already exists.");
            
        } 

		frm.clear_table("items")
		frm.refresh_field("items")
    },
	accepted_quantity:function(frm,cdt,cdn) {
		const child = locals[cdt][cdn];
		console.log("$$$$$$$$$$$$$$")
		child.received_quantity = child.accepted_quantity + child.rejected_quantity
		refresh_field("received_quantity",cdn,"items")
	}
	
});

frappe.ui.form.on("Purchase Details", {
	accepted_quantity:function(frm,cdt,cdn) {
		const child = locals[cdt][cdn];
		console.log("$$$$$$$$$$$$$$")
		child.received_quantity = child.accepted_quantity + child.rejected_quantity
		refresh_field("received_quantity",cdn,"items")
		if ((child.accepted_quantity + child.rejected_quantity) > child.qty) {
			// child.accepted_quantity = 0
			// child.received_quantity = 0
			// refresh_field("received_quantity",cdn,"items")
			// refresh_field("accepted_quantity",cdn,"items")
			// frappe.throw("Received Qty can't be greater than the Purchase Order Qty")
		}
		if (child.received_quantity > (child.qty - child.actual_received_qty)) {
			// child.accepted_quantity = 0
			// child.received_quantity = 0
			// refresh_field("received_quantity",cdn,"items")
			// refresh_field("accepted_quantity",cdn,"items")
			// frappe.throw("Received Qty can't be greater than the Purchase Order Qty");
		}
	},
	rejected_quantity:function(frm,cdt,cdn) {
		const child = locals[cdt][cdn];
		child.received_quantity = child.accepted_quantity + child.rejected_quantity
		refresh_field("received_quantity",cdn,"items")
		if ((child.accepted_quantity + child.rejected_quantity) > child.qty) {
			// child.rejected_quantity = 0
			child.received_quantity = child.accepted_quantity + child.rejected_quantity
			// refresh_field("received_quantity",cdn,"items")
			// refresh_field("rejected_quantity",cdn,"items")
			// frappe.throw("Received Qty can't be greater than the Purchase Order Qty")
		}
		if (child.received_quantity > (child.qty - child.actual_received_qty)) {
			// child.accepted_quantity = 0
			// child.received_quantity = 0
			// refresh_field("received_quantity",cdn,"items")
			// refresh_field("accepted_quantity",cdn,"items")
			// frappe.throw("Received Qty can't be greater than the Purchase Order Qty");
		}
	}
	
});