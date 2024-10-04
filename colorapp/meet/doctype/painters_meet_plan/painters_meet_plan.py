# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaintersMeetPlan(Document):

    def validate(self):
        # Ensure no member is added more than once
        self.ensure_unique_members()

    def ensure_unique_members(self):
        """Check if a member is added more than once in the invite table"""
        member_list = []
        for invite in self.painters_meet_invite:
            if invite.colour_academy_member in member_list:  # Use correct field name
                frappe.throw(f"Member {invite.colour_academy_member} is already in the invite list. Please avoid duplicates.")
            member_list.append(invite.colour_academy_member)  # Use correct field name

    def before_submit(self):
        # Ensure the invitees table is not empty during the submit process
        if not self.get('painters_meet_invite'):
            frappe.throw("You must add at least one invitee before submitting the document.")
