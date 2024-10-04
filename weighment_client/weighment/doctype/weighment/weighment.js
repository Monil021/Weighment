// Copyright (c) 2024, Dexciss Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.provide("weighment_client.play_audio");
weighment_client.play_audio = function(audio_profile) {
    frappe.call({
        method: "weighment_client.weighment_client_utils.play_audio",
        args: {
            audio_profile: audio_profile
        },
        callback: function(r) {
            if (r.message) {
            }
        }
    });
};


frappe.ui.form.on("Weighment", {
	refresh: function (frm) {
        frm.disable_save();
        frm.events.check_weighbridge_is_empty(frm);
        // frm.events.wake_up_screen_event(frm);
	},

    check_weighbridge_is_empty: function (frm) {
        frm.call({
            method: "check_weighbridge_is_empty",
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    frappe.show_alert({message:__("Weight loss Detected"), indicator:'green'});
                    frm.events.wake_up_screen_event(frm);
                }
            }
        })
    },

    wake_up_screen_event:function(frm){
        frappe.call({
            method: "wake_up_screen",
            doc: frm.doc,
            callback: function (r) {
                if(r.message){
                    frappe.show_alert({message:__("Weight Gain Detected"), indicator:'green'});
                    frm.events.check_for_card(frm);
                }  
            },
        }) 
    },

    check_for_card: function (frm) {
        frm.call({
            method: "fetch_card_details",
            doc: frm.doc,
            callback: function (r) {
                console.log("hex code:------->",r.message)
                if (r.message) {
                    frm.events.check_card_validations(frm, r.message)
                }
            }
        })
    },

    check_card_validations: function (frm, hex_code) {
        frm.call({
            method: "check_card_validations",
            doc:frm.doc,
            args: {
                hex_code: hex_code
            },
            callback: function (r) {
                console.log("response msg:------>",r.message)
                if (r.message && r.message === "trigger_empty_card_validation" || r.message && r.message === "trigger weight loss") {
                    frm.events.is_card_removed_already(frm);
                    return
                }

                if (r.message && r.message === "weighment_already_done") {
                    frappe.call({
                        method: "validate_card_number",
                        doc: frm.doc,
                        callback: function (r) {
                            if (r.message) {
                                frm.events.is_card_removed_already(frm);
                                return
                            }
                        }
                    })
                }

                if (r.message && r.message === "trigger_empty_delivery_note_validation") {
                    frappe.call({
                        method: "empty_delivery_note_validatin",
                        doc: frm.doc,
                        callback: function (r) {
                            if (r.message) {
                                frm.events.is_card_removed_already(frm);
                                return
                            }
                        }
                    })
                }

                if (r.message && r.message.gate_entry) {
                    frm.set_value("gate_entry_number", r.message.gate_entry);
                    frm.refresh_field("gate_entry_number");
                    var message = "Received Card Number: " + r.message.gate_entry;
                    frappe.show_alert({ message: __(message), indicator: 'green' });

                }

                
            }
        })
    },





     


    // check_for_card: function(frm) {
    //     console.log("triggered function ==> check_for_card")
    //     var audioIntervalID = null;
    
    //     function playAudio(message) {
    //         console.log(message);
    //         weighment_client.play_audio("Please put your card on machine");
    //     }
    
    //     function stopAudio() {
    //         clearInterval(audioIntervalID);
    //     }
    
    //     playAudio("Waiting for response...");
    
    //     frappe.call({
    //         method: "fetch_gate_entry",
    //         doc: frm.doc,
    //         callback: function(r) {

    //             console.log("***************",r.message)
    //             stopAudio();
    //             if (r.message === "weighment_already_done") {
    //                 stopAudio();
    //                 frm.events.validate_card_number(frm);
    //                 return
    //             }else if (r.message === "trigger_empty_card_validation"){
    //                 stopAudio();
    //                 frm.events.is_card_removed_already(frm);
    //                 return
    //             }else if (r.message == "trigger weight loss"){
    //                 stopAudio();
    //                 frm.events.is_card_removed_already(frm);
    //                 return
    //             }else if (r.message == "trigger_empty_delivery_note_validation") {
    //                 stopAudio();
    //                 frm.events.empty_delivery_note(frm);
    //                 return
    //             }
    //             else if (r.message && r.message.gate_entry) {

                    // frm.set_value("gate_entry_number", r.message.gate_entry);
                    // frm.refresh_field("gate_entry_number");
                    // var message = "Received Card Number: " + r.message.gate_entry;
                    // frappe.show_alert({ message: __(message), indicator: 'green' });
    //                 stopAudio();

    //             }
    //             else {
    //                 stopAudio();
    //                 frm.events.needs_reweighment(frm);
    //             }
    //         }
    //     });
    
    //     audioIntervalID = setInterval(function() {
    //         playAudio("Still waiting for response...");
    //     }, 6000);
    
    //     frm.cscript.on_close = function() {
    //         clearInterval(audioIntervalID);
    //         stopAudio();
    //     };
    // },

    validate_card_number:function(frm){
        console.log("triggered function ==>, validate_card_number ")
        frappe.call({
            method: "validate_card_number",
            doc: frm.doc,
            callback: function(r) {
                console.log("responce from the validate_card_number ==> ",r.message)
                if (r.message) {
                    frm.events.is_card_removed_already(frm);
                }
            }
        });
    },

    gate_entry_number: function(frm) {
        if (frm.doc.gate_entry_number) {
            frappe.run_serially([

                () => frm.trigger("map_data_by_card"),

                () => frm.trigger("check_for_button")
            ]);
        }
    
    },

    empty_delivery_note:function(frm) {
        frappe.call({
            method:"empty_delivery_note_validatin",
            doc:frm.doc,
            callback:function(r) {
                if (r.message) {
                    frm.events.is_card_removed_already(frm);
                }
            }
        })
    },

    map_data_by_card: function (frm) {
        frm.call({
            method: "map_data_by_card",
            doc: frm.doc,
            freeze: true,
			freeze_message: __("Getting Data ..."),

            callback: function (r) {
                if (r.message) {
                    frm.refresh_fields()
                }
            }
        })
    },

    needs_reweighment: function(frm) {
        frappe.call({
            method:"needs_reweighment",
            doc:frm.doc,
            callback:function(r) {
                if (r.message) {
                    frm.events.is_card_removed_already(frm);
                }
            }
        })
    },

    check_for_button: function (frm) {
        frm.call({
            method: "check_for_button",
            doc:frm.doc,
            callback: function (r) {
                if (r.message) {
                    frappe.show_alert({message:__("Button Press Detected"), indicator:'green'});
                    frm.events.proceed_button_press_event(frm)
                }
            }
        })
    },

    proceed_button_press_event: function (frm) {
        frappe.call({
            method:"is_new_weighment_record",
            doc:frm.doc,
            args:{
                entry:frm.doc.gate_entry_number
            },
            callback:function(r){                            
                if (r.message && r.message === "no_weighment_record_found"){
                    console.log("creating new entry")
                    frappe.run_serially([
                        () => frm.trigger("update_weight_details_for_new_entry_record"),
                        () => frm.trigger("create_new_weighment_entry"),
                    ]);


                } else if (r.message && r.message === "existing_record_found"){
                    console.log("updating existing entry")
                    frappe.run_serially([
                        () => frm.trigger("update_weight_details_for_existing_entry_record"),
                        // () => frm.trigger("print_second_slip"),
                        () => frm.trigger("update_existing_weighment_record"),
                    ]);
                    // clearInterval(audioIntervalID);
                    // stopAudio();

                } else if (r.message && "need_reweighment") {
                    // clearInterval(audioIntervalID);
                    // stopAudio();
                    frm.trigger("needs_reweighment")
                }
                else {
                    // clearInterval(audioIntervalID);
                    // stopAudio();
                    frm.trigger("needs_reweighment")
                }
            }
        })

    },

    // check_for_button:function(frm){
    //     console.log("called function ==> check_for_button")
    //     var audioIntervalID = null;
    
    //     function playAudio(message) {
    //         console.log(message);
    //         weighment_client.play_audio("Press green button for weight");
    //     }
    
    //     function stopAudio() {
    //         clearInterval(audioIntervalID);
    //     }

    //     playAudio("Waiting for response...");
    
    //     audioIntervalID = setInterval(function() {
    //         playAudio("Still waiting for response...");
    //     }, 9000);

    //     frappe.call({
    //         // method:"is_button_precessed",
    //         method:"weighment_client.weighment_client_utils.read_button_switch",
    //         // doc:frm.doc,
    //         callback:function(r){    
    //             console.log("callback from check_for_button ==>",r.message)            
    //             if (r.message){
    //                 frappe.show_alert({message:__("Button Press Detected"), indicator:'green'});
                    // frappe.call({
                    //     method:"is_new_weighment_record",
                    //     doc:frm.doc,
                    //     args:{
                    //         entry:frm.doc.gate_entry_number
                    //     },
                    //     callback:function(r){                            
                    //         if (r.message && r.message === "no_weighment_record_found"){
                    //             console.log("creating new entry")
                    //             frappe.run_serially([
                    //                 () => frm.trigger("update_weight_details_for_new_entry_record"),
                    //                 () => frm.trigger("create_new_weighment_entry"),
                    //             ]);
                    //             clearInterval(audioIntervalID);
                    //             stopAudio();

                    //         } else if (r.message && r.message === "existing_record_found"){
                    //             console.log("updating existing entry")
                    //             frappe.run_serially([
                    //                 () => frm.trigger("update_weight_details_for_existing_entry_record"),
                    //                 // () => frm.trigger("print_second_slip"),
                    //                 () => frm.trigger("update_existing_weighment_record"),
                    //             ]);
                    //             clearInterval(audioIntervalID);
                    //             stopAudio();

                    //         } else if (r.message && "need_reweighment") {
                    //             clearInterval(audioIntervalID);
                    //             stopAudio();
                    //             frm.trigger("needs_reweighment")
                    //         }
                    //         else {
                    //             clearInterval(audioIntervalID);
                    //             stopAudio();
                    //             frm.trigger("needs_reweighment")
                    //         }
                    //     }
                    // })
    //             }
    //         },
    //     })
    // },

    update_weight_details_for_new_entry_record:function(frm){
        console.log("frm.doc.referece_record:--->",frm.doc.gate_entry_number)

        frappe.call({
            method:"update_weight_details_for_new_entry",
            doc:frm.doc,
            args:{
                entry:frm.doc.gate_entry_number
            },
            callback:function(r){
                frm.refresh_fields()
                console.log("Updated weight field...")
            }
        })
    },

    create_new_weighment_entry:function(frm){
        frappe.call({
            method:"create_new_weighment_entry",
            doc:frm.doc,
            callback:function(r){
                if(r.message && r.message === "weight_done"){
                    frappe.show_alert({message:__("New Record Created"), indicator:'green'});
                    // frm.events.remove_card_from_machine(frm)
                    // frm.events.is_weighbridge_empty(frm)
                    frappe.run_serially([
                        // () => frm.trigger("print_first_slip"),
                        () => frm.trigger("is_card_removed_already"), 
                    ]);    
                } else if (r.message && r.message === "needs_reweight") {
                    frappe.show_alert({message:__("Needs reweight"), indicator:'red'});
                    // frm.events.remove_card_from_machine(frm)
                    // frm.events.is_weighbridge_empty(frm)
                    frappe.run_serially([
                        () => frm.trigger("needs_reweighment"),
                        () => frm.trigger("is_card_removed_already"), 
                    ]);    
                }
            }
        })
    },

    update_weight_details_for_existing_entry_record:function(frm){
        frappe.call({
            method:"update_weight_details_for_existing_entry",
            doc:frm.doc,
            callback:function(r){
                console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",r.message)
                if (r.message === "trigger_weight_validation"){
                    // frm.events.is_weighbridge_empty(frm)
                    // frm.events.remove_card_from_machine(frm)
                    frm.events.is_card_removed_already(frm)
                    return

                }
                else if (r.message === "trigger_delivery_note_validation"){
                    console.log("^^^^^^^^triggered delivery note validation")
                    frm.events.is_card_removed_already(frm)
                    return false
                }

                frm.refresh_fields()
            }
        })
    },

    update_existing_weighment_record:function(frm){
        console.log("triggered method ==> update_existing_weighment_record")      
        frappe.call({
            method:"update_existing_weighment_details",
            doc:frm.doc,
            callback:function(r){
                
                if (r.message && r.message === "weight_done") {
                    console.log("recived callback from update_existing_weighment_record ==>",r.message)
                    frappe.run_serially([
                        // () => frm.trigger("print_second_slip"),
                        () => frm.trigger("is_card_removed_already"), 
                    ]); 
                } else if (r.message && r.message === "needs_reweight") {
                    frappe.show_alert({message:__("Needs reweight"), indicator:'red'});
                    frappe.run_serially([
                        () => frm.trigger("needs_reweighment"),
                        () => frm.trigger("is_card_removed_already"), 
                    ]);
                }       
            }
        })
    },

    is_card_removed_already:function(frm){
        console.log("triggered function:---> is_card_removed_already")
        frappe.call({
            method:"weighment_client.weighment_client_utils.is_card_removed_already",
            callback:function(r){
                if (r.message == "card removed") {
                    console.log("responce from is_card_removed_already if condition ==>",r.message)
                    frm.events.is_weighbridge_empty(frm);
                }else if (r.message == "card not removed") {
                    console.log("responce from is_card_removed_already else condition ==>",r.message)
                    frm.events.remove_card_from_machine(frm);
                    // frm.events.remove_card_from_machine_and_check_empty(frm);
                }
            }
        })
    },

    remove_card_from_machine: function (frm) {
        frm.call({
            method: "remove_card_from_machine",
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    frm.events.is_weighbridge_empty(frm);
                }
            }
        })
    },



    // remove_card_from_machine: function(frm) {
    //     console.log("triggered function ==>, remove_card_from_machine ")
    //     var audioIntervalID = null;
    
    //     function playAudio(message) {
    //         console.log(message);
    //         weighment_client.play_audio("Please remove your card");
    //     }
    
    //     function stopAudio() {
    //         clearInterval(audioIntervalID);
    //     }
    //     playAudio("Waiting for response...");
    
    //     audioIntervalID = setInterval(function() {
    //         playAudio("Still waiting for response...");
    //     }, 6000);
    
    //     frappe.call({
            
    //         method: "weighment_client.weighment_client_utils.check_card_removed",
    //         callback: function(r) {
    //             console.log("responce from ==> remove_card_from_machine", r.message);
    //             if (!r.message) {
    //                 clearInterval(audioIntervalID);
    //                 stopAudio();
    //                 frm.events.is_weighbridge_empty(frm);
    //             }
    //         }
    //     });
    // },

    is_weighbridge_empty: function(frm) {
        console.log("triggered function ==>, is_weighbridge_empty")
        var audioIntervalID = null;
    
        function playAudio(message) {
            console.log(message);
            weighment_client.play_audio("Clear platform for next weight");
        }
    
        function stopAudio() {
            clearInterval(audioIntervalID);
        }
    
        playAudio("Waiting for response...");
    
        audioIntervalID = setInterval(function() {
            playAudio("Still waiting for response...");
        }, 6000);
    
        frappe.call({
            method: "clear_plateform_for_next_weighment",
            doc: frm.doc,
            callback: function(r) {
                if (r.message) {
                    console.log("responce from the function is_weighbridge_empty ==>",r.message);
                    frappe.show_alert({ message: __("Weight loss Detected"), indicator: 'green' });
                    clearInterval(audioIntervalID);
                    stopAudio();
                    
                    // localStorage.removeItem('weighment_screen_active');
                    frm.reload_doc()
                }
            },
        });
    },
})
