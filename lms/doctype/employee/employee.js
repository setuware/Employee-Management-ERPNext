frappe.ui.form.on('Employee', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Leave Requests'), function() {
				frappe.set_route('List', 'Leave Request', {'employee': frm.doc.name});
			});
		}
	},
	
	employee_id: function(frm) {
		if (frm.doc.employee_id) {
			frm.set_value('employee_id', frm.doc.employee_id.toUpperCase());
		}
	},
	
	email: function(frm) {
		if (frm.doc.email) {
			frm.set_value('email', frm.doc.email.toLowerCase());
		}
	}
});
