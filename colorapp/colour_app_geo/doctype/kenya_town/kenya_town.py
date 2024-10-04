# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class KenyaTown(Document):
    def before_insert(self):
        # Generate the town_code series
        self.town_code = make_autoname('KT-.####')
        # Set the town_code as the name of the document
        self.name = self.town_code
