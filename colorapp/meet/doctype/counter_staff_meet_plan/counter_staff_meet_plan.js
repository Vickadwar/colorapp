// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Counter Staff Meet Plan', {
    refresh: function(frm) {
        // Check if the document is submitted and attendance has not been created
        if (frm.doc.docstatus == 1 && !frm.doc.attendance_created) {
            frm.add_custom_button(__('Create Attendance'), function() {
                // Call the backend method to create attendance
                frappe.call({
                    method: 'colorapp.api.create_counter_staff_meet_attendance',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Attendance created successfully'));
                            // Redirect to the newly created attendance document
                            frappe.set_route("Form", "Counter Staff Meet Attendance", r.message);
                            frm.reload_doc();  // Reload the form after attendance creation to hide the button
                        }
                    }
                });
            });
        }
    },

    // Trigger when a dealer is added to dynamically filter counter staff linked to the dealers
    dealers_meet_invite_add: function(frm) {
        frm.trigger('set_counter_staff_filters');
    },

    // Function to apply filters based on the dealers added to the dealers_meet_invite table
    set_counter_staff_filters: function(frm) {
        let dealer_list = frm.doc.dealers_meet_invite.map(row => row.dealer_name);
        
        if (dealer_list.length) {
            frm.fields_dict['counter_staff_meet_invite'].grid.get_field('counter_staff_name').get_query = function() {
                return {
                    filters: [
                        ['Counter Staff Member', 'primary_dealer', 'in', dealer_list]
                    ]
                };
            };
        } else {
            frm.fields_dict['counter_staff_meet_invite'].grid.get_field('counter_staff_name').get_query = function() {
                return {};  // No filter if no dealers are added
            };
        }
    },

    // Ensure the filter is applied when the form is loaded
    onload: function(frm) {
        frm.trigger('set_counter_staff_filters');
    }
});
