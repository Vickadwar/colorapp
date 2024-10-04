# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.model.document import Document

class CounterStaffMember(Document):

    def before_insert(self):
        # Generate the 8-digit random number for member_app_number
        if not self.member_app_number:
            self.member_app_number = self.generate_unique_member_app_number()

        # Set the document name to the member_app_number
        self.name = self.member_app_number

    def before_save(self):
        # Concatenate first_name, second_name, and last_name into counter_staff_name
        self.counter_staff_name = self.combine_names(self.first_name, self.second_name, self.last_name)

        # Validate unique mobile number
        self.validate_unique_mobile_number()

    def combine_names(self, first_name, second_name, last_name):
        # Combine the names, skipping any None values
        name_parts = [first_name, second_name, last_name]
        # Filter out any None or empty string values, then join them with a space
        return " ".join(filter(None, name_parts))

    def validate_unique_mobile_number(self):
        # Check if mobile_number is present and validate uniqueness
        if self.mobile_number:
            # Check if another member has the same mobile number
            existing_member = frappe.db.exists(
                "Counter Staff Member", {"mobile_number": self.mobile_number, "name": ("!=", self.name)}
            )
            if existing_member:
                frappe.throw(f"The mobile number {self.mobile_number} is already associated with another member.")

    def generate_unique_member_app_number(self):
        # Generate a random 8-digit number
        member_app_number = random.randint(10000000, 99999999)
        # Ensure the generated number is unique
        while frappe.db.exists("Counter Staff Member", {"member_app_number": str(member_app_number)}):
            member_app_number = random.randint(10000000, 99999999)
        return str(member_app_number)
