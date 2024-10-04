# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MerchandiseEntryDetail(Document):
    def validate(self):
        if not self.merchandise_item:
            frappe.throw(_("Merchandise Item is required"))

        if self.quantity <= 0:
            frappe.throw(_("Quantity must be greater than zero"))
