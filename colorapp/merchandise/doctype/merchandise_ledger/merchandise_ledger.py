# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class MerchandiseLedger(Document):
    
    def before_insert(self):
        # This method is called before inserting a new ledger entry
        self.update_balance()

    def update_balance(self):
        # Update the balance based on previous ledger entries
        # Ensure you're using the correct field 'merchandise_item_code' instead of 'merchandise_item'
        last_entry = frappe.db.get_value(
            "Merchandise Ledger",
            {
                "merchandise_item_code": self.merchandise_item_code,  # Corrected field
                "merchandise_warehouse": self.merchandise_warehouse
            },
            "balance_after"
        )

        # Set the balance after based on the last entry
        if last_entry:
            self.balance_after = last_entry + self.quantity
        else:
            # If no previous entry exists, the balance starts with the current quantity
            self.balance_after = self.quantity
