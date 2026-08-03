let currentTaskPage = 1;
let totalTaskPages = 1;

frappe.ready(function() {
	loadEmployeeOptions();
	loadTasks(1);
	loadTaskSummary();
});

function loadEmployeeOptions() {
	frappe.call({
		method: 'lms.api.employee.get_employees_options',
		callback: function(r) {
			if (!r.message || !r.message.success) return;
			r.message.data.forEach(function(emp) {
				document.getElementById('task-assignee').innerHTML +=
					'<option value="' + emp.name + '">' + emp.full_name + ' (' + emp.employee_id + ')</option>';
			});
		}
	});
}

function loadTaskSummary() {
	frappe.call({
		method: 'lms.api.task.get_task_summary',
		callback: function(r) {
			if (!r.message || !r.message.success) return;
			const s = r.message.data;
			document.getElementById('sum-total').textContent = s.total;
			document.getElementById('sum-progress').textContent = s.in_progress;
			document.getElementById('sum-completed').textContent = s.completed;
			document.getElementById('sum-hours').textContent = s.total_hours;
		}
	});
}

function loadTasks(page) {
	currentTaskPage = page;
	const args = {
		page: page,
		page_size: 20
	};
	const status = document.getElementById('task-filter-status').value;
	if (status) args.status = status;

	frappe.call({
		method: 'lms.api.task.get_tasks',
		args: args,
		callback: function(r) {
			const tbody = document.getElementById('tasks-tbody');
			tbody.innerHTML = '';
			if (!r.message || !r.message.success) {
				frappe.show_alert({message: r.message ? r.message.message : 'Error loading tasks', indicator: 'red'});
				return;
			}
			totalTaskPages = r.message.total_pages;

			r.message.data.forEach(function(task) {
				const tr = document.createElement('tr');
				tr.innerHTML = [
					'<td><strong>' + task.title + '</strong><br><small>' + (task.task_id || '') + '</small></td>',
					'<td>' + task.assigned_to_name + '</td>',
					'<td>' + task.priority + '</td>',
					'<td>' + statusSelect(task) + '</td>',
					'<td>' + (task.due_date || '-') + '</td>',
					'<td>' + (task.total_time || '0.00') + '</td>',
					'<td>' + timerButton(task) + '</td>',
					'<td><button class="sw-btn sw-btn-danger sw-btn-sm" onclick="deleteTask(\'' + task.name + '\')">Delete</button></td>'
				].join('');
				tbody.appendChild(tr);
			});

			renderPagination();
		}
	});
}

function statusSelect(task) {
	return '<select class="status-select" onchange="updateTaskStatus(\'' + task.name + '\', this.value)">' +
		['Not Started', 'In Progress', 'Completed', 'Cancelled'].map(function(s) {
			return '<option' + (s === task.status ? ' selected' : '') + '>' + s + '</option>';
		}).join('') +
		'</select>';
}

function timerButton(task) {
	if (task.timer_running) {
		return '<button class="sw-btn sw-btn-danger sw-btn-sm" onclick="stopTimer(\'' + task.name + '\')">Stop</button>';
	}
	return '<button class="sw-btn sw-btn-primary sw-btn-sm" onclick="startTimer(\'' + task.name + '\')">Start Timer</button>';
}

function updateTaskStatus(name, status) {
	frappe.call({
		method: 'lms.api.task.update_task',
		args: { name: name, data: { status: status } },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadTasks(currentTaskPage);
				loadTaskSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
				loadTasks(currentTaskPage);
			}
		}
	});
}

function startTimer(name) {
	frappe.call({
		method: 'lms.api.task.start_timer',
		args: { task: name },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadTasks(currentTaskPage);
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function stopTimer(name) {
	frappe.call({
		method: 'lms.api.task.stop_timer',
		args: { task: name },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadTasks(currentTaskPage);
				loadTaskSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function createTask() {
	const data = {
		title: document.getElementById('task-title').value,
		description: document.getElementById('task-description').value,
		assigned_to: document.getElementById('task-assignee').value,
		priority: document.getElementById('task-priority').value,
		due_date: document.getElementById('task-due').value,
		estimated_hours: document.getElementById('task-est-hours').value
	};

	if (!data.title) {
		frappe.show_alert({message: 'Task title is required', indicator: 'red'});
		return;
	}

	frappe.call({
		method: 'lms.api.task.create_task',
		args: { data: data },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				document.getElementById('task-title').value = '';
				document.getElementById('task-description').value = '';
				document.getElementById('task-due').value = '';
				document.getElementById('task-est-hours').value = '';
				loadTasks(1);
				loadTaskSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function deleteTask(name) {
	if (!confirm('Delete this task?')) return;
	frappe.call({
		method: 'lms.api.task.delete_task',
		args: { name: name },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadTasks(currentTaskPage);
				loadTaskSummary();
			} else if (r.message) {
				frappe.show_alert({message: r.message.message, indicator: 'red'});
			}
		}
	});
}

function renderPagination() {
	const el = document.getElementById('tasks-pagination');
	el.innerHTML = '';
	if (currentTaskPage > 1) {
		el.innerHTML += '<button class="sw-btn sw-btn-sm" onclick="loadTasks(' + (currentTaskPage - 1) + ')">Prev</button> ';
	}
	el.innerHTML += '<span>Page ' + currentTaskPage + ' of ' + totalTaskPages + '</span>';
	if (currentTaskPage < totalTaskPages) {
		el.innerHTML += ' <button class="sw-btn sw-btn-sm" onclick="loadTasks(' + (currentTaskPage + 1) + ')">Next</button>';
	}
}
