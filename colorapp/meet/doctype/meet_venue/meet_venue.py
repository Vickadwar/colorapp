# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class MeetVenue(Document):
    def before_insert(self):
        # Generate meet_venue_code series
        self.meet_venue_code = make_autoname('CPK-MV.####')
        # Set the meet_venue_code as the name of the document
        self.name = self.meet_venue_code

