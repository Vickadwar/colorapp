// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Merchandise Entry', {
    onload: function(frm) {
        // Auto-populate posting_date and posting_time
        if (!frm.doc.posting_date) {
            frm.set_value('posting_date', frappe.datetime.get_today());
        }

        if (!frm.doc.posting_time) {
            frm.set_value('posting_time', frappe.datetime.now_time());
        }

        // Set posting_datetime when form is loaded
        frm.trigger('set_posting_datetime');
    },

    posting_date: function(frm) {
        frm.trigger('set_posting_datetime');
    },

    posting_time: function(frm) {
        frm.trigger('set_posting_datetime');
    },

    set_posting_datetime: function(frm) {
        if (frm.doc.posting_date && frm.doc.posting_time) {
            let posting_datetime = `${frm.doc.posting_date} ${frm.doc.posting_time}`;
            frm.set_value('posting_datetime', posting_datetime);
        }
    },

    merchandise_entry_type: function(frm) {
        frm.trigger('toggle_warehouses_visibility');
        frm.trigger('filter_warehouses');
    },

    toggle_warehouses_visibility: function(frm) {
        // Show/hide source and target warehouses based on entry type
        if (frm.doc.merchandise_entry_type === "Merchandise Issue") {
            frm.set_df_property('source_warehouse', 'hidden', false); // Show Source Warehouse
            frm.set_df_property('target_warehouse', 'hidden', true);  // Hide Target Warehouse
        } else if (frm.doc.merchandise_entry_type === "Merchandise Receipt") {
            frm.set_df_property('source_warehouse', 'hidden', true);  // Hide Source Warehouse
            frm.set_df_property('target_warehouse', 'hidden', false); // Show Target Warehouse
        } else if (frm.doc.merchandise_entry_type === "Merchandise Transfer") {
            frm.set_df_property('source_warehouse', 'hidden', false); // Show Source Warehouse
            frm.set_df_property('target_warehouse', 'hidden', false); // Show Target Warehouse
        }
    },

    filter_warehouses: function(frm) {
        if (frm.doc.target_warehouse) {
            frm.set_query("source_warehouse", function() {
                return {
                    filters: {
                        name: ["!=", frm.doc.target_warehouse]
                    }
                };
            });
        }

        if (frm.doc.source_warehouse) {
            frm.set_query("target_warehouse", function() {
                return {
                    filters: {
                        name: ["!=", frm.doc.source_warehouse]
                    }
                };
            });
        }
    }
});

// Child table interactivity for fetching balance
frappe.ui.form.on('Merchandise Entry Detail', {
    merchandise_item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Only fetch stock balance for Issue or Transfer
        if (frm.doc.merchandise_entry_type === "Merchandise Issue" || frm.doc.merchandise_entry_type === "Merchandise Transfer") {
            if (frm.doc.source_warehouse && row.merchandise_item_code) {
                frappe.call({
                    method: "colorapp.api.get_item_balance",  // Calls server-side function
                    args: {
                        "item_code": row.merchandise_item_code,
                        "warehouse": frm.doc.source_warehouse
                    },
                    callback: function(response) {
                        if (response.message) {
                            let balance = response.message;
                            frappe.model.set_value(cdt, cdn, "quantity", balance);  // Set balance in quantity field
                            frappe.show_alert({
                                message: `Available stock for ${row.merchandise_item_code} in ${frm.doc.source_warehouse}: ${balance}`,
                                indicator: 'blue'
                            });
                        }
                    }
                });
            }
        }
    }
});
