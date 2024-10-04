// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Counter Staff Meet Attendance', {
    refresh: function(frm) {
        // Add the button only if the document is submitted
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Download Meet Attendance List'), function() {
                // Call the backend function to download the Excel file
                frappe.call({
                    method: 'colorapp.api.download_counter_staff_meet_attendance_excel',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(response) {
                        // Handle the file download
                        if (response.message) {
                            var link = document.createElement('a');
                            link.href = response.message;
                            link.download = 'Counter_Staff_Meet_Attendance_List_' + frm.doc.name + '.xlsx';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }
                    }
                });
            });
        }
    }
});
