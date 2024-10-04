# Copyright (c) 2024, Victor Mandela and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class CPKRegion(Document):
    def before_insert(self):
        # Generate the region_code series
        self.region_code = make_autoname('CPK-R.###')
        # Set the region_code as the name of the document
        self.name = self.region_code
