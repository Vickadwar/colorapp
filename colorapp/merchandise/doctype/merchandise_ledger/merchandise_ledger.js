// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt


frappe.ui.form.on('Merchandise Ledger', {
    onload: function(frm) {
        if(frm.doc.reference_doctype && frm.doc.reference_docname) {
            frappe.db.get_value(frm.doc.reference_doctype, frm.doc.reference_docname, 'merchandise_entry_type', (r) => {
                frm.set_value('transaction_type', r.merchandise_entry_type);
            });
        }
    }
});

