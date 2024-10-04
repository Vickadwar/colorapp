// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Merchandise Entry Detail', {
    merchandise_item_code: function(frm, cdt, cdn) {
        var item = locals[cdt][cdn];

        // Fetch the merchandise item name based on the item code
        frappe.db.get_value('Merchandise Item', item.merchandise_item_code, 'item_name', function(value) {
            frappe.model.set_value(cdt, cdn, 'merchandise_item_name', value.item_name);
        });
    }
});
