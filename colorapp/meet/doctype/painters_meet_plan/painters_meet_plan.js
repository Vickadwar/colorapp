// Copyright (c) 2024, Victor Mandela and contributors
// For license information, please see license.txt

frappe.ui.form.on('Painters Meet Plan', {
    refresh: function(frm) {
        console.log('Form refreshed');

        // Set pagination on the child table to show 10 rows per page
        frm.fields_dict['painters_meet_invite'].grid.page_length = 10;
        frm.fields_dict['painters_meet_invite'].grid.refresh();

        // Add "Add Row" button first (this is Frappe's default behavior)
        // We don't need to manually add it as Frappe adds it automatically.

        // Add "Upload Invitees" button
        frm.fields_dict['painters_meet_invite'].grid.add_custom_button(__('Upload Invitees'), function() {
            // Automatically save the form if it hasn't been saved yet
            if (frm.is_dirty() || frm.doc.__islocal) {
                frappe.show_alert({
                    message: __('Saving the document before uploading invitees...'),
                    indicator: 'blue'
                });

                frm.save().then(function() {
                    // After saving, proceed with the file upload
                    initiate_invitees_upload(frm);
                });
            } else {
                // If the form is already saved, proceed with the file upload
                initiate_invitees_upload(frm);
            }
        }).css({ 'background-color': '#00008b', 'color': 'white' }); // Dark blue styling for Upload Invitees

        // Add "Download Template" button
        frm.fields_dict['painters_meet_invite'].grid.add_custom_button(__('Download Template'), function() {
            // Call the backend method to download the template
            window.open('/api/method/colorapp.api.download_invitees_template');
        });

        // Add "Create Attendance" button if the document is submitted and attendance is not yet created
        if (frm.doc.docstatus == 1 && !frm.doc.attendance_created) {
            frm.add_custom_button(__('Create Attendance'), function() {
                frappe.call({
                    method: 'colorapp.api.create_painters_meet_attendance',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Attendance created successfully'));
                            frappe.set_route("Form", "Painters Meet Attendance", r.message);
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
    },

    // Detect changes in the child table grid
    painters_meet_invite: {
        grid: {
            on_form_rendered: function(frm, cdt, cdn) {
                check_for_duplicates(frm);
            }
        }
    }
});

function initiate_invitees_upload(frm) {
    const file_input = $('<input type="file" accept=".xls,.xlsx">');
    file_input.on('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const binary_data = e.target.result;  // Get the binary string content directly
                frappe.call({
                    method: 'colorapp.api.upload_invitees',
                    args: {
                        file_data: binary_data,  // Send the binary string content
                        plan_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint(__('Invitees uploaded successfully'));
                            frm.reload_doc(); // Reload to refresh the child table
                        }
                    }
                });
            };
            reader.readAsBinaryString(file);  // Read file as binary string
        }
    });
    file_input.click(); // Trigger the file selection dialog
}

// Function to check for duplicate members in the child table
function check_for_duplicates(frm) {
    console.log('Checking for duplicates');

    let members = frm.doc.painters_meet_invite || [];
    let member_set = new Set();
    let duplicate_found = false;

    members.forEach(function(row) {
        console.log('Checking member: ', row.colour_academy_member);
        if (member_set.has(row.colour_academy_member)) {
            frappe.msgprint(__('Duplicate member {0} found. Please remove the duplicate.', [row.colour_academy_member]));
            duplicate_found = true;
        }
        member_set.add(row.colour_academy_member);
    });

    if (duplicate_found) {
        frm.disable_save();
    } else {
        frm.enable_save();
    }
}
