let currentEmployeePage = 1;
let currentLeavePage = 1;
const pageSize = 10;

frappe.ready(function() {
	loadDepartments();
	loadEmployees();
	loadLeaveRequests();
	loadSummary();
});

function showTab(tabName) {
	document.querySelectorAll('.tab-content').forEach(tab => {
		tab.style.display = 'none';
	});
	document.querySelectorAll('.tab-btn').forEach(btn => {
		btn.classList.remove('active');
	});
	
	document.getElementById(tabName).style.display = 'block';
	
	const buttons = document.querySelectorAll('.tab-btn');
	buttons.forEach((btn, index) => {
		const tabNames = ['employee-list', 'leave-requests', 'summary-report'];
		if (tabNames[index] === tabName) {
			btn.classList.add('active');
		}
	});
	
	if (tabName === 'summary-report') {
		loadSummary();
	} else if (tabName === 'leave-requests') {
		loadLeaveRequests(currentLeavePage);
	} else if (tabName === 'employee-list') {
		loadEmployees(currentEmployeePage);
	}
}

function loadDepartments() {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Department',
			fields: ['name']
		},
		callback: function(r) {
			const select = document.getElementById('department');
			r.message.forEach(dept => {
				const option = document.createElement('option');
				option.value = dept.name;
				option.textContent = dept.name;
				select.appendChild(option);
			});
		}
	});
}

function loadEmployees(page = 1, search = '') {
	currentEmployeePage = page;
	frappe.call({
		method: 'lms.api.employee.get_employees',
		args: {
			page: page,
			page_size: pageSize,
			search_term: search
		},
		callback: function(r) {
			if (r.message.success) {
				renderEmployees(r.message.data);
				renderPagination('employee-pagination', r.message, loadEmployees);
			} else {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function renderEmployees(employees) {
	const tbody = document.getElementById('employee-tbody');
	tbody.innerHTML = '';
	
	employees.forEach(emp => {
		const row = document.createElement('tr');
		row.innerHTML = `
			<td>${emp.employee_id || ''}</td>
			<td><img src="${emp.profile_picture || '/assets/frappe/images/ui/avatar.png'}" class="profile-img" alt="Profile"></td>
			<td>${emp.full_name || ''}</td>
			<td>${emp.email || ''}</td>
			<td>${emp.department || ''}</td>
			<td>${emp.joining_date || ''}</td>
			<td><button class="btn-icon" onclick="editEmployee('${emp.name}')">✏️</button></td>
		`;
		tbody.appendChild(row);
	});
}

function searchEmployees() {
	const search = document.getElementById('employee-search').value;
	loadEmployees(1, search);
}

function showAddEmployeeForm() {
	document.getElementById('form-title').textContent = 'Add Employee';
	resetForm();
}

function editEmployee(name) {
	frappe.call({
		method: 'lms.api.employee.get_employee',
		args: { name: name },
		callback: function(r) {
			if (r.message.success) {
				const emp = r.message.data;
				document.getElementById('employee-name').value = emp.name;
				document.getElementById('employee-id').value = emp.employee_id || '';
				document.getElementById('full-name').value = emp.full_name || '';
				document.getElementById('email').value = emp.email || '';
				document.getElementById('login-password').value = '';
				document.getElementById('department').value = emp.department || '';
				document.getElementById('joining-date').value = emp.joining_date || '';
				document.getElementById('profile-picture').value = emp.profile_picture || '';
				
				if (emp.profile_picture) {
					document.getElementById('profile-preview').src = emp.profile_picture;
					document.getElementById('profile-preview').style.display = 'block';
				}
				
				document.getElementById('form-title').textContent = 'Edit Employee';
			}
		}
	});
}

function saveEmployee(event) {
	event.preventDefault();
	
	const formData = {
		employee_id: document.getElementById('employee-id').value,
		full_name: document.getElementById('full-name').value,
		email: document.getElementById('email').value,
		department: document.getElementById('department').value,
		joining_date: document.getElementById('joining-date').value,
		profile_picture: document.getElementById('profile-picture').value,
		password: document.getElementById('login-password').value
	};
	
	const name = document.getElementById('employee-name').value;
	const method = name ? 'lms.api.employee.update_employee' : 'lms.api.employee.create_employee';
	const args = name ? { name: name, data: formData } : { data: formData };
	
	frappe.call({
		method: method,
		args: args,
		callback: function(r) {
			if (r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				resetForm();
				loadEmployees(currentEmployeePage);
			} else {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function resetForm() {
	document.getElementById('employee-form').reset();
	document.getElementById('employee-name').value = '';
	document.getElementById('profile-preview').style.display = 'none';
	document.getElementById('form-title').textContent = 'Add Employee';
}

function uploadProfilePicture() {
	const dialog = new frappe.ui.Dialog({
		title: 'Upload Profile Picture',
		fields: [
			{
				label: 'Attach Image',
				fieldname: 'image',
				fieldtype: 'Attach Image'
			}
		],
		primary_action_label: 'Upload',
		primary_action: function() {
			const image = dialog.get_value('image');
			if (image) {
				document.getElementById('profile-picture').value = image;
				document.getElementById('profile-preview').src = image;
				document.getElementById('profile-preview').style.display = 'block';
				dialog.hide();
			}
		}
	});
	dialog.show();
}

function loadLeaveRequests(page = 1, search = '', status = '') {
	currentLeavePage = page;
	frappe.call({
		method: 'lms.api.leave_request.get_leave_requests',
		args: {
			page: page,
			page_size: pageSize,
			search_term: search,
			status: status
		},
		callback: function(r) {
			if (r.message.success) {
				renderLeaveRequests(r.message.data);
				renderPagination('leave-pagination', r.message, loadLeaveRequests);
			}
		}
	});
}

function renderLeaveRequests(requests) {
	const tbody = document.getElementById('leave-tbody');
	tbody.innerHTML = '';
	
	requests.forEach(req => {
		const row = document.createElement('tr');
		const statusClass = req.status.toLowerCase();
		row.innerHTML = `
			<td>${req.leave_id || ''}</td>
			<td>
				<img src="${req.employee_profile || '/assets/frappe/images/ui/avatar.png'}" class="profile-img-small" alt="Profile">
				${req.employee_name || req.employee || ''}
			</td>
			<td>${req.leave_type || ''}</td>
			<td>${req.from_date || ''}</td>
			<td>${req.to_date || ''}</td>
			<td><span class="status-badge ${statusClass}">${req.status || ''}</span></td>
		`;
		tbody.appendChild(row);
	});
}

function searchLeaveRequests() {
	const search = document.getElementById('leave-search').value;
	const status = document.getElementById('status-filter').value;
	loadLeaveRequests(1, search, status);
}

function filterLeaveRequests() {
	const search = document.getElementById('leave-search').value;
	const status = document.getElementById('status-filter').value;
	loadLeaveRequests(1, search, status);
}

function loadSummary() {
	frappe.call({
		method: 'lms.api.leave_request.get_summary',
		callback: function(r) {
			if (r.message.success) {
				const data = r.message.data;
				document.getElementById('total-leaves').textContent = data.total_leaves || 0;
				document.getElementById('approved-leaves').textContent = data.approved_leaves || 0;
				document.getElementById('pending-leaves').textContent = data.pending_leaves || 0;
				document.getElementById('canceled-leaves').textContent = data.canceled_leaves || 0;
			}
		}
	});
}

function exportCSV() {
	frappe.call({
		method: 'lms.api.leave_request.export_csv',
		callback: function(r) {
			if (r.message.success) {
				window.open(r.message.file_url, '_blank');
				frappe.show_alert({message: 'CSV exported successfully', indicator: 'green'});
			} else {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function renderPagination(elementId, paginationData, callback) {
	const pagination = document.getElementById(elementId);
	if (!pagination) return;
	
	pagination.innerHTML = '';
	
	if (paginationData.total_pages <= 1) return;
	
	const currentPage = paginationData.page;
	const totalPages = paginationData.total_pages;
	
	if (currentPage > 1) {
		const prevBtn = document.createElement('button');
		prevBtn.textContent = 'Previous';
		prevBtn.className = 'btn btn-secondary';
		prevBtn.onclick = () => callback(currentPage - 1);
		pagination.appendChild(prevBtn);
	}
	
	const pageInfo = document.createElement('span');
	pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
	pageInfo.className = 'page-info';
	pagination.appendChild(pageInfo);
	
	if (currentPage < totalPages) {
		const nextBtn = document.createElement('button');
		nextBtn.textContent = 'Next';
		nextBtn.className = 'btn btn-secondary';
		nextBtn.onclick = () => callback(currentPage + 1);
		pagination.appendChild(nextBtn);
	}
}
