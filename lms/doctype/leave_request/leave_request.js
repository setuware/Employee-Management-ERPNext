frappe.ui.form.on('Leave Request', {
	refresh: function(frm) {
		if (frm.doc.status === 'Pending' && frappe.user.has_role('HR Manager')) {
			frm.add_custom_button(__('Approve'), function() {
				frm.set_value('status', 'Approved');
				frm.save();
			}, __('Actions'));
			
			frm.add_custom_button(__('Reject'), function() {
				frm.set_value('status', 'Rejected');
				frm.save();
			}, __('Actions'));
		}
		
		if (frm.doc.status === 'Pending' && !frappe.user.has_role('HR Manager')) {
			frm.add_custom_button(__('Cancel'), function() {
				frm.set_value('status', 'Canceled');
				frm.save();
			}, __('Actions'));
		}
	},
	
	from_date: function(frm) {
		if (frm.doc.from_date && frm.doc.to_date) {
			if (frm.doc.to_date < frm.doc.from_date) {
				frappe.msgprint(__('To Date cannot be before From Date'));
				frm.set_value('to_date', '');
			}
		}
	},
	
	to_date: function(frm) {
		if (frm.doc.from_date && frm.doc.to_date) {
			if (frm.doc.to_date < frm.doc.from_date) {
				frappe.msgprint(__('To Date cannot be before From Date'));
				frm.set_value('to_date', '');
			}
		}
	}
});
