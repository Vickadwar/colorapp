# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class MerchandiseEntryType(Document):

    def validate(self):
        if not self.merchandise_entry_type_name:
            frappe.throw(_("Merchandise Entry Type Name is required"))

        if not self.merchandise_entry_type:
            frappe.throw(_("Merchandise Entry Type is required"))

        # Ensure valid entry types are selected
        valid_types = ["Merchandise Issue", "Merchandise Receipt", "Merchandise Transfer"]
        if self.merchandise_entry_type not in valid_types:
            frappe.throw(_("Invalid Merchandise Entry Type"))

        # Call specific validation for the selected entry type
        if self.merchandise_entry_type == "Merchandise Receipt":
            self.validate_receipt()
        elif self.merchandise_entry_type == "Merchandise Issue":
            self.validate_issue()
        elif self.merchandise_entry_type == "Merchandise Transfer":
            self.validate_transfer()

    def validate_transfer(self):
        """Validation logic specific to Merchandise Transfer"""
        if not self.source_warehouse:
            frappe.throw(_("Source Warehouse is required for Merchandise Transfer"))
        if not self.target_warehouse:
            frappe.throw(_("Target Warehouse is required for Merchandise Transfer"))
        if self.source_warehouse == self.target_warehouse:
            frappe.throw(_("Source Warehouse and Target Warehouse cannot be the same"))

        # Additional rules for Merchandise Transfer can go here
        frappe.msgprint(_("Validated Merchandise Transfer"))


