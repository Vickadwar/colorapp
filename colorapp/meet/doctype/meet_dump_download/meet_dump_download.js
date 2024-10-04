// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Meet Dump Download', {
    download_type: function(frm) {
        // Reset field visibility
        frm.set_df_property('meet_type', 'hidden', false);
        frm.set_df_property('select_painters_meet', 'hidden', true);
        frm.set_df_property('select_counter_staff_meet', 'hidden', true);
        frm.set_df_property('from_date', 'hidden', true);
        frm.set_df_property('to_date', 'hidden', true);

        if (frm.doc.download_type === "Single Meet") {
            frm.set_df_property('meet_type', 'reqd', true);
            frm.set_df_property('select_painters_meet', 'hidden', false);
            frm.set_df_property('select_counter_staff_meet', 'hidden', false);
        } else if (frm.doc.download_type === "Multiple Meets") {
            frm.set_df_property('meet_type', 'reqd', true);
            frm.set_df_property('from_date', 'hidden', false);
            frm.set_df_property('to_date', 'hidden', false);
        } else if (frm.doc.download_type === "Painters Dump" || frm.doc.download_type === "Counter Staff Dump") {
            frm.set_df_property('from_date', 'hidden', false);
            frm.set_df_property('to_date', 'hidden', false);
            frm.set_df_property('meet_type', 'hidden', true);
            frm.set_df_property('select_painters_meet', 'hidden', true);
            frm.set_df_property('select_counter_staff_meet', 'hidden', true);
        } else {
            // Reset all fields
            frm.set_df_property('meet_type', 'reqd', false);
        }
    },

    meet_type: function(frm) {
        if (frm.doc.download_type === "Single Meet") {
            if (frm.doc.meet_type === "Painters Meet") {
                frm.set_df_property('select_painters_meet', 'hidden', false);
                frm.set_df_property('select_counter_staff_meet', 'hidden', true);
            } else if (frm.doc.meet_type === "Counter Staff Meet") {
                frm.set_df_property('select_counter_staff_meet', 'hidden', false);
                frm.set_df_property('select_painters_meet', 'hidden', true);
            }
        }
    },

    refresh: function(frm) {
        frm.add_custom_button(__('Download Data'), function() {
            if (frm.doc.download_type === "Single Meet") {
                if (frm.doc.meet_type === "Painters Meet") {
                    frappe.call({
                        method: 'colorapp.api.download_single_meet_painters',
                        args: {
                            meet_name: frm.doc.select_painters_meet,
                            docname: frm.doc.name  // Pass the current document name
                        },
                        callback: function(r) {
                            if (r.message) {
                                window.open(r.message);  // Open the download link
                            }
                        }
                    });
                } else if (frm.doc.meet_type === "Counter Staff Meet") {
                    frappe.call({
                        method: 'colorapp.api.download_single_meet_counter_staff',
                        args: {
                            meet_name: frm.doc.select_counter_staff_meet,
                            docname: frm.doc.name  // Pass the current document name
                        },
                        callback: function(r) {
                            if (r.message) {
                                window.open(r.message);  // Open the download link
                            }
                        }
                    });
                }
            } else if (frm.doc.download_type === "Multiple Meets") {
                frappe.call({
                    method: 'colorapp.api.download_multiple_meets',
                    args: {
                        meet_type: frm.doc.meet_type,
                        from_date: frm.doc.from_date,
                        to_date: frm.doc.to_date,
                        docname: frm.doc.name  // Pass the current document name
                    },
                    callback: function(r) {
                        if (r.message) {
                            window.open(r.message);  // Open the download link
                        }
                    }
                });
            } else if (frm.doc.download_type === "Painters Dump") {
                frappe.call({
                    method: 'colorapp.api.download_painters_dump',
                    args: {
                        from_date: frm.doc.from_date,
                        to_date: frm.doc.to_date,
                        docname: frm.doc.name  // Pass the current document name
                    },
                    callback: function(r) {
                        if (r.message) {
                            window.open(r.message);  // Open the download link
                        }
                    }
                });
            } else if (frm.doc.download_type === "Counter Staff Dump") {
                frappe.call({
                    method: 'colorapp.api.download_counter_staff_dump',
                    args: {
                        from_date: frm.doc.from_date,
                        to_date: frm.doc.to_date,
                        docname: frm.doc.name  // Pass the current document name
                    },
                    callback: function(r) {
                        if (r.message) {
                            window.open(r.message);  // Open the download link
                        }
                    }
                });
            }
        });
    }
});
