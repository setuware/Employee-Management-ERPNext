frappe.ui.form.on('LMS Task', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.timer_running) {
			frm.add_custom_button(__('Stop Timer'), function() {
				frappe.call({
					method: 'lms.api.task.stop_timer',
					args: { task: frm.doc.name },
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
		} else if (!frm.is_new() && !frm.doc.timer_running) {
			frm.add_custom_button(__('Start Timer'), function() {
				frappe.call({
					method: 'lms.api.task.start_timer',
					args: { task: frm.doc.name },
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
