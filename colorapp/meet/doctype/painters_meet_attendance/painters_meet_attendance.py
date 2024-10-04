# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from collections import defaultdict

class PaintersMeetAttendance(Document):

    def validate(self):
        # Ensure the gifts are valid before submission and automatically update gift_issued status
        self.validate_and_update_gifts()

        # Ensure training supplies are valid
        self.validate_training_supplies()

        # Automatically fetch and assign the user's merchandise warehouse
        if not self.user_merchandise_warehouse:
            self.user_merchandise_warehouse = frappe.db.get_value("User", frappe.session.user, "merchandise_warehouse")
            if not self.user_merchandise_warehouse:
                frappe.throw(_("You are not assigned a Merchandise Warehouse"))

    def validate_and_update_gifts(self):
        """
        Ensure that if a gift is issued, the respective quantities are set correctly.
        Also ensure that gift_one and gift_two are not the same on the same row.
        Automatically update the `gift_issued` status based on whether gifts have been provided.
        """
        for entry in self.attendance_list:
            # Update the gift_issued status based on the gift fields
            if (entry.gift_one and entry.qty > 0) or (entry.gift_two and entry.qnty > 0):
                entry.gift_issued = 'Yes'
            else:
                entry.gift_issued = 'No'

            if entry.gift_issued == 'Yes':
                # Ensure that gift_one and gift_two are not the same
                if entry.gift_one and entry.gift_two and entry.gift_one == entry.gift_two:
                    frappe.throw(_("Gift One and Gift Two cannot be the same for {0}".format(entry.member_name)))

                # Validate quantities for gifts if they are filled
                if entry.gift_one and entry.qty <= 0:
                    frappe.throw(_("Please specify the quantity for Gift One for {0}".format(entry.member_name)))
                
                if entry.gift_two and entry.qnty <= 0:
                    frappe.throw(_("Please specify the quantity for Gift Two for {0}".format(entry.member_name)))
            else:
                # If no gift is issued, allow empty gift fields and zero quantities
                entry.gift_one = None
                entry.qty = 0
                entry.gift_two = None
                entry.qnty = 0

    def validate_training_supplies(self):
        """
        Ensure that training supplies are valid before submission.
        - Quantity must be greater than 0 for each entry.
        - No duplicate items should be added.
        """
        seen_items = []
        for supply in self.training_supplies:
            if not supply.training_supply_name:
                frappe.throw(_("Please select a supply item in the Training Supplies table."))

            if supply.training_supply_name in seen_items:
                frappe.throw(_("Item {0} is already added in the Training Supplies table. Please remove the duplicate entry.".format(supply.training_supply_name)))

            if supply.quantity <= 0:
                frappe.throw(_("Please enter a valid quantity for item {0}. Quantity cannot be zero or negative.".format(supply.training_supply_name)))

            seen_items.append(supply.training_supply_name)

    def on_submit(self):
        # Create Merchandise Entry of type Issue for the gifts and training supplies
        merchandise_entry = None

        # Dictionary to store total consumption per item
        consumption_summary = defaultdict(float)

        # Iterate over the attendance list and process issued gifts
        for entry in self.attendance_list:
            if entry.gift_issued == 'Yes':
                # Process Gift One
                if entry.gift_one and entry.qty > 0:
                    if not merchandise_entry:
                        merchandise_entry = self.create_merchandise_entry()
                    self.add_gift_to_merchandise_entry(merchandise_entry, entry.gift_one, entry.qty)
                    consumption_summary[entry.gift_one] += entry.qty  # Update consumption summary

                # Process Gift Two
                if entry.gift_two and entry.qnty > 0:
                    if not merchandise_entry:
                        merchandise_entry = self.create_merchandise_entry()
                    self.add_gift_to_merchandise_entry(merchandise_entry, entry.gift_two, entry.qnty)
                    consumption_summary[entry.gift_two] += entry.qnty  # Update consumption summary

        # Process Training Supplies
        for supply in self.training_supplies:
            if supply.training_supply_name and supply.quantity > 0:
                if not merchandise_entry:
                    merchandise_entry = self.create_merchandise_entry()
                self.add_gift_to_merchandise_entry(merchandise_entry, supply.training_supply_name, supply.quantity)
                consumption_summary[supply.training_supply_name] += supply.quantity  # Update consumption summary

        # Submit the Merchandise Entry if any gifts or supplies were processed
        if merchandise_entry:
            merchandise_entry.submit()

        # Update the Meet Merchandise Issue Detail table with the summarized consumption
        self.update_merchandise_consumption(consumption_summary)

    def create_merchandise_entry(self):
        """
        Create a Merchandise Entry document for type Issue, linked to the session user's warehouse.
        """
        return frappe.get_doc({
            'doctype': 'Merchandise Entry',
            'merchandise_entry_type': 'Merchandise Issue',
            'posting_date': frappe.utils.today(),
            'posting_time': frappe.utils.nowtime(),
            'source_warehouse': self.user_merchandise_warehouse,  # Fetch warehouse from session user
            'merchandise_entry_description': "Gifts and supplies issued during the Painters Meet"
        })

    def add_gift_to_merchandise_entry(self, merchandise_entry, gift, quantity):
        """
        Add each gift issued to the merchandise entry.
        """
        merchandise_entry.append('merchandise_items', {
            'merchandise_item_code': gift,
            'quantity': quantity
        })

    def update_merchandise_consumption(self, consumption_summary):
        """
        Update the Meet Merchandise Issue Detail table with summarized merchandise consumption.
        """
        self.merchandise_consumption = []  # Clear previous entries

        for item_name, consumed_quantity in consumption_summary.items():
            self.append('merchandise_consumption', {
                'merchandise_item_name': item_name,
                'consumed_quantity': consumed_quantity
            })
