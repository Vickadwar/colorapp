# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

class MerchandiseEntry(Document):

    def validate(self):
        # Validate necessary warehouses based on the entry type
        if self.merchandise_entry_type == "Merchandise Issue" and not self.source_warehouse:
            frappe.throw(_("Source Warehouse is required for Merchandise Issue"))
        if self.merchandise_entry_type == "Merchandise Receipt" and not self.target_warehouse:
            frappe.throw(_("Target Warehouse is required for Merchandise Receipt"))
        if self.merchandise_entry_type == "Merchandise Transfer":
            if not self.source_warehouse:
                frappe.throw(_("Source Warehouse is required for Merchandise Transfer"))
            if not self.target_warehouse:
                frappe.throw(_("Target Warehouse is required for Merchandise Transfer"))
            if self.source_warehouse == self.target_warehouse:
                frappe.throw(_("Source and Target Warehouse cannot be the same for Merchandise Transfer"))

        # Validate stock availability for Issue and Transfer
        if self.merchandise_entry_type in ["Merchandise Issue", "Merchandise Transfer"]:
            self.validate_stock_levels()

        # Validate that items and quantities are selected
        for item in self.merchandise_items:
            if not item.merchandise_item_code:
                frappe.throw(_("Merchandise Item is required"))
            if item.quantity <= 0:
                frappe.throw(_("Quantity must be greater than zero"))

    def validate_stock_levels(self):
        """
        This function checks if the available stock is sufficient in the source warehouse 
        before allowing Issue or Transfer.
        """
        for item in self.merchandise_items:
            available_qty = self.get_item_balance(item.merchandise_item_code, self.source_warehouse)
            if available_qty < item.quantity:
                frappe.throw(_(
                    "Insufficient stock for {0} in {1}. Available: {2}, Required: {3}"
                ).format(item.merchandise_item_name, self.source_warehouse, available_qty, item.quantity))

    def get_item_balance(self, item_code, warehouse):
        """
        Fetches the latest stock balance from the Merchandise Ledger for a given item and warehouse.
        """
        last_entry = frappe.db.get_value("Merchandise Ledger", 
            {"merchandise_item_code": item_code, "merchandise_warehouse": warehouse}, 
            "balance_after", order_by="posting_datetime desc"
        )
        return last_entry or 0  # Return 0 if no previous stock entry is found

    def on_submit(self):
        # Handle stock ledger updates on submit based on merchandise entry type
        self.update_stock_ledger()

    def on_cancel(self):
        # Reverse the stock ledger when cancelling
        self.update_stock_ledger(cancel=True)

    def update_stock_ledger(self, cancel=False):
        multiplier = -1 if cancel else 1
        for item in self.merchandise_items:
            if self.merchandise_entry_type == "Merchandise Receipt":
                self.create_ledger_entry(item, self.target_warehouse, multiplier, cancel)
            elif self.merchandise_entry_type == "Merchandise Issue":
                self.create_ledger_entry(item, self.source_warehouse, -multiplier, cancel)
            elif self.merchandise_entry_type == "Merchandise Transfer":
                # Remove from source and add to target warehouse
                self.create_ledger_entry(item, self.source_warehouse, -multiplier, cancel)
                self.create_ledger_entry(item, self.target_warehouse, multiplier, cancel)

    def create_ledger_entry(self, item, warehouse, multiplier, cancel):
        qty = item.quantity * multiplier
        balance_qty = self.get_item_balance(item.merchandise_item_code, warehouse) + qty

        # Create a Merchandise Ledger entry
        ledger_entry = frappe.get_doc({
            "doctype": "Merchandise Ledger",
            "merchandise_item_code": item.merchandise_item_code,
            "merchandise_warehouse": warehouse,
            "posting_date": self.posting_date,
            "posting_time": self.posting_time,
            "posting_datetime": frappe.utils.now(),
            "quantity": qty,
            "balance_after": balance_qty,
            "transaction_type": self.merchandise_entry_type,
            "reference_doc_name": self.name,
            "transaction_remarks": self.merchandise_entry_description or f"{self.merchandise_entry_type}",
            "is_cancelled": 1 if cancel else 0  # Use the passed cancel variable here
        })
        ledger_entry.insert()

        # After updating the ledger, update the warehouse balances and check for stock level alerts
        self.update_warehouse_merchandise_item(item, warehouse, qty)

    def update_warehouse_merchandise_item(self, item, warehouse, qty):
        """
        Updates the balance_quantity in the Warehouse Merchandise Detail child table
        in the Merchandise Warehouse Doctype based on stock movement (issue, transfer, receipt).
        """
        warehouse_doc = frappe.get_doc("Merchandise Warehouse", warehouse)
        found = False

        for detail in warehouse_doc.merchandise_warehouse_item:
            if detail.merchandise_item_code == item.merchandise_item_code:
                # Update the balance quantity
                detail.balance_quantity += qty
                found = True
                # Check stock level after transaction
                self.check_stock_level_after_transaction(item.merchandise_item_code, detail.balance_quantity, warehouse)
                break

        if not found and qty > 0:
            warehouse_doc.append("merchandise_warehouse_item", {
                "merchandise_item_code": item.merchandise_item_code,
                "merchandise_item_name": item.merchandise_item_name,
                "balance_quantity": qty
            })

        warehouse_doc.save()

    def check_stock_level_after_transaction(self, item_code, balance_quantity, warehouse):
        """
        Checks if the stock level of an item falls below the minimum stock level after the transaction.
        If it does, it triggers a system notification and optionally an email notification.
        """
        merchandise_item = frappe.get_doc("Merchandise Item", item_code)

        if balance_quantity < merchandise_item.minimum_stock_level:
            warehouse_doc = frappe.get_doc("Merchandise Warehouse", warehouse)
            user = frappe.db.get_value("User", {"merchandise_warehouse": warehouse_doc.name}, "email")

            # Create a system notification
            self.create_system_notification(user, merchandise_item, balance_quantity, warehouse)

    def create_system_notification(self, user, merchandise_item, balance_quantity, warehouse):
        """
        Creates a system notification for the user when stock falls below the minimum level.
        """
        # Corrected field name to 'merchandise_item_name'
        message = (f"Stock for item {merchandise_item.merchandise_item_name} in warehouse {warehouse} is below the minimum level. "
                f"Current balance: {balance_quantity}. Please reorder or create a merchandise request.")

        # Notification content
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"Low Stock Alert for {merchandise_item.merchandise_item_name}",
            "email_content": message,
            "for_user": user,
            "document_type": "Merchandise Item",  # Link the notification to the Merchandise Item
            "document_name": merchandise_item.name  # Link the item in the notification
        })
        notification.insert(ignore_permissions=True)


        # Optional: send an email (uncomment this when email setup is ready)
        # frappe.sendmail(
        #     recipients=[user],
        #     subject=f"Low Stock Alert for {merchandise_item.item_name}",
        #     message=message
        # )