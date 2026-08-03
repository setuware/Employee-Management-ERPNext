frappe.ui.form.on('LMS Attendance', {
	refresh: function(frm) {
		if (frm.doc.check_in && !frm.doc.check_out) {
			frm.add_custom_button(__('Check Out'), function() {
				frappe.call({
					method: 'lms.api.attendance.check_out',
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.show_alert({message: r.message.message, indicator: 'green'});
							frm.reload_doc();
						} else if (r.message) {
							frappe.show_alert({message: r.message.message, indicator: 'red'});
						}
					}
				});
			}, __('Actions'));
		}
	}
});
