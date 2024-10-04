# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random
from datetime import datetime, timedelta

class ColourAppMember(Document):

    def before_insert(self):
        # Auto-generate the member_app_number if not set
        if not self.member_app_number:
            self.member_app_number = self.generate_unique_membership_number()

        if not self.name:
            self.autoname()
            
    def before_save(self):
        # Combine first_name, second_name, and last_name into member_name
        self.member_name = self.combine_names(self.first_name, self.second_name, self.last_name)
        
        # Ensure the mobile_number is unique
        self.validate_unique_mobile_number()

        # Ensure the national_id is unique
        self.validate_unique_national_id()

        # Ensure the tk_membership_number is unique
        self.validate_unique_tk_membership_number()

        # Validate the date of birth
        self.validate_age()

    def combine_names(self, first_name, second_name, last_name):
        name_parts = [first_name, second_name, last_name]
        combined_name = " ".join(filter(None, name_parts))
        return combined_name

    def generate_unique_membership_number(self):
        number = random.randint(10000000, 99999999)
        while frappe.db.exists('ColourAppMember', {'member_app_number': str(number)}):
            number = random.randint(10000000, 99999999)
        return str(number)

    def autoname(self):
        self.name = self.member_app_number

    def validate_unique_mobile_number(self):
        if self.mobile_number:
            # Use SQL query to check for duplicate mobile numbers
            existing_member = frappe.db.sql("""
                SELECT name FROM `tabColour App Member`
                WHERE mobile_number = %s AND name != %s
            """, (self.mobile_number, self.name))

            if existing_member:
                frappe.throw(f"The mobile number {self.mobile_number} is already associated with another member.")
    
    def validate_unique_national_id(self):
        if self.id_number:
            # Use SQL query to check for duplicate national ID numbers
            existing_member = frappe.db.sql("""
                SELECT name FROM `tabColour App Member`
                WHERE id_number = %s AND name != %s
            """, (self.id_number, self.name))

            if existing_member:
                frappe.throw(f"The national ID {self.id_number} is already associated with another member.")

    def validate_unique_tk_membership_number(self):
        if self.tk_membership_number:
            # Use SQL query to check for duplicate tk_membership_number
            existing_member = frappe.db.sql("""
                SELECT name FROM `tabColour App Member`
                WHERE tk_membership_number = %s AND name != %s
            """, (self.tk_membership_number, self.name))

            if existing_member:
                frappe.throw(f"The TK Membership Number {self.tk_membership_number} is already associated with another member.")
    
    def validate_age(self):
        if self.date_of_birth:
            try:
                # Convert the date_of_birth from string to datetime.date
                if isinstance(self.date_of_birth, str):
                    self.date_of_birth = datetime.strptime(self.date_of_birth, '%Y-%m-%d').date()
                elif isinstance(self.date_of_birth, datetime):
                    self.date_of_birth = self.date_of_birth.date()

                today = datetime.today().date()
                age = today - self.date_of_birth
                if age < timedelta(days=365 * 18):
                    frappe.throw("Member must be at least 18 years old to register.")
            except Exception as e:
                frappe.throw(f"Error parsing date of birth: {str(e)}")
