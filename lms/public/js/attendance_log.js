let currentLogPage = 1;
let totalLogPages = 1;

frappe.ready(function() {
	document.getElementById('record-date').value = new Date().toISOString().slice(0, 10);
	document.getElementById('filter-date').value = new Date().toISOString().slice(0, 10);
	loadEmployeeOptions();
	loadLog(1);
	loadSummary();
});

function loadEmployeeOptions() {
	frappe.call({
		method: 'lms.api.employee.get_employees_options',
		callback: function(r) {
			if (!r.message || !r.message.success) return;
			const options = r.message.data;
			options.forEach(function(emp) {
				const label = emp.full_name + ' (' + emp.employee_id + ')';
				document.getElementById('filter-employee').innerHTML += '<option value="' + emp.name + '">' + label + '</option>';
				document.getElementById('record-employee').innerHTML += '<option value="' + emp.name + '">' + label + '</option>';
			});
		}
	});
}

function loadSummary() {
	frappe.call({
		method: 'lms.api.attendance.get_attendance_summary',
		callback: function(r) {
			if (!r.message || !r.message.success) return;
			const s = r.message.data;
			document.getElementById('sum-total').textContent = s.total_employees;
			document.getElementById('sum-in').textContent = s.checked_in;
			document.getElementById('sum-absent').textContent = s.absent;
			document.getElementById('sum-hours').textContent = s.total_hours;
		}
	});
}

function loadLog(page) {
	currentLogPage = page;
	const args = {
		page: page,
		page_size: 20
	};
	if (document.getElementById('filter-date').value) args.date = document.getElementById('filter-date').value;
	if (document.getElementById('filter-employee').value) args.employee = document.getElementById('filter-employee').value;
	if (document.getElementById('filter-status').value) args.status = document.getElementById('filter-status').value;

	frappe.call({
		method: 'lms.api.attendance.get_attendance_log',
		args: args,
		callback: function(r) {
			const tbody = document.getElementById('log-tbody');
			tbody.innerHTML = '';
			if (!r.message || !r.message.success) {
				frappe.show_alert({message: r.message ? r.message.message : 'Error loading log', indicator: 'red'});
				return;
			}
			totalLogPages = r.message.total_pages;

			r.message.data.forEach(function(att) {
				const tr = document.createElement('tr');
				tr.innerHTML = [
					'<td>' + att.attendance_date + '</td>',
					'<td><strong>' + att.employee_name + '</strong><br><small>' + (att.employee_id || '') + '</small></td>',
					'<td>' + (att.check_in ? new Date(att.check_in).toLocaleString() : '-') + '</td>',
					'<td>' + (att.check_out ? new Date(att.check_out).toLocaleString() : '-') + '</td>',
					'<td>' + (att.work_hours || '0.00') + '</td>',
					'<td><span class="status-badge ' + String(att.status || '').toLowerCase().replace(/\s+/g, '_') + '">' + att.status + '</span></td>',
					'<td>' + att.source + '</td>',
					'<td><button class="sw-btn sw-btn-danger sw-btn-sm" onclick="deleteRecord(\'' + att.name + '\')">Delete</button></td>'
				].join('');
				tbody.appendChild(tr);
			});

			renderPagination();
		}
	});
}

function renderPagination() {
	const el = document.getElementById('log-pagination');
	el.innerHTML = '';
	if (currentLogPage > 1) {
		el.innerHTML += '<button class="sw-btn sw-btn-sm" onclick="loadLog(' + (currentLogPage - 1) + ')">Prev</button> ';
	}
	el.innerHTML += '<span>Page ' + currentLogPage + ' of ' + totalLogPages + '</span>';
	if (currentLogPage < totalLogPages) {
		el.innerHTML += ' <button class="sw-btn sw-btn-sm" onclick="loadLog(' + (currentLogPage + 1) + ')">Next</button>';
	}
}

function recordAttendance() {
	const data = {
		employee: document.getElementById('record-employee').value,
		attendance_date: document.getElementById('record-date').value,
		check_in: document.getElementById('record-check-in').value,
		check_out: document.getElementById('record-check-out').value,
		status: document.getElementById('record-status').value,
		notes: document.getElementById('record-notes').value
	};

	if (!data.employee || !data.attendance_date) {
		frappe.show_alert({message: 'Select an employee and date', indicator: 'red'});
		return;
	}

	frappe.call({
		method: 'lms.api.attendance.record_attendance',
		args: { data: data },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				document.getElementById('record-check-in').value = '';
				document.getElementById('record-check-out').value = '';
				document.getElementById('record-notes').value = '';
				loadLog(currentLogPage);
				loadSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function deleteRecord(name) {
	if (!confirm('Delete this attendance record?')) return;
	frappe.call({
		method: 'lms.api.attendance.delete_attendance',
		args: { name: name },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadLog(currentLogPage);
				loadSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}
