let runningTimerTick = null;

frappe.ready(function() {
	loadProfile();
	loadToday();
	loadMySummary();
	loadMyTasks();
	loadHistory();
	loadMyLeaves();
});

function showError(msg) {
	frappe.show_alert({message: msg, indicator: 'red'});
}

function loadProfile() {
	frappe.call({
		method: 'lms.api.employee.get_my_profile',
		callback: function(r) {
			if (r.message && r.message.success) {
				const emp = r.message.data;
				document.getElementById('portal-name').textContent = emp.full_name + ' (' + emp.employee_id + ')';
				document.getElementById('portal-sub').textContent = emp.department ? emp.department + ' Department' : 'Employee';
			} else if (r.message) {
				document.getElementById('no-employee-warning').style.display = 'block';
			}
		}
	});
}

function loadToday() {
	frappe.call({
		method: 'lms.api.attendance.get_today',
		callback: function(r) {
			const statusEl = document.getElementById('att-status');
			if (!r.message || !r.message.success) {
				statusEl.textContent = 'Unavailable';
				return;
			}
			const att = r.message.data;
			if (!att) {
				statusEl.textContent = 'Not Checked In Yet';
				document.getElementById('btn-check-in').style.display = 'inline-block';
				return;
			}
			statusEl.textContent = att.status;
			document.getElementById('att-check-in').textContent = att.check_in ? new Date(att.check_in).toLocaleTimeString() : '--:--';
			document.getElementById('att-check-out').textContent = att.check_out ? new Date(att.check_out).toLocaleTimeString() : '--:--';
			document.getElementById('att-work-hours').textContent = att.work_hours || '0.00';

			if (!att.check_out) {
				document.getElementById('btn-check-out').style.display = 'inline-block';
			}
		}
	});
}

function doCheckIn() {
	frappe.call({
		method: 'lms.api.attendance.check_in',
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadToday();
				loadMySummary();
				loadHistory();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}

function doCheckOut() {
	frappe.call({
		method: 'lms.api.attendance.check_out',
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadToday();
				loadMySummary();
				loadHistory();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}

function loadMySummary() {
	frappe.call({
		method: 'lms.api.attendance.get_my_summary',
		callback: function(r) {
			if (r.message && r.message.success) {
				const s = r.message.data;
				document.getElementById('sum-present').textContent = s.present_days;
				document.getElementById('sum-hours').textContent = s.total_hours;
				document.getElementById('sum-late').textContent = s.lates;
			}
		}
	});

	frappe.call({
		method: 'lms.api.task.get_task_summary',
		callback: function(r) {
			if (r.message && r.message.success) {
				const s = r.message.data;
				document.getElementById('sum-tasks').textContent = s.total - s.completed - s.cancelled;
			}
		}
	});
}

function loadMyTasks() {
	frappe.call({
		method: 'lms.api.task.get_my_tasks',
		callback: function(r) {
			const tbody = document.getElementById('my-tasks-tbody');
			tbody.innerHTML = '';
			if (!r.message || !r.message.success || !r.message.data.length) {
				document.getElementById('my-tasks-empty').style.display = 'block';
				document.getElementById('my-tasks-table').style.display = 'none';
				return;
			}
			document.getElementById('my-tasks-empty').style.display = 'none';
			document.getElementById('my-tasks-table').style.display = 'table';

			r.message.data.forEach(function(task) {
				const tr = document.createElement('tr');
				tr.innerHTML = [
					'<td><strong>' + task.title + '</strong></td>',
					'<td>' + task.priority + '</td>',
					'<td><span class="status-badge ' + String(task.status).toLowerCase().replace(/\s+/g, '_') + '">' + task.status + '</span></td>',
					'<td>' + (task.due_date || '-') + '</td>',
					'<td class="task-time" id="time-' + task.name + '">' + (task.total_time || '0.00') + '</td>',
					'<td>' + timerButton(task) + '</td>'
				].join('');
				tbody.appendChild(tr);
			});

			startElapsedTicker(r.message.data);
		}
	});
}

function timerButton(task) {
	if (task.timer_running) {
		return '<button class="sw-btn sw-btn-danger sw-btn-sm" onclick="stopTimer(\'' + task.name + '\')">Stop</button>';
	}
	return '<button class="sw-btn sw-btn-primary sw-btn-sm" onclick="startTimer(\'' + task.name + '\')">Start Timer</button>';
}

function startTimer(taskName) {
	frappe.call({
		method: 'lms.api.task.start_timer',
		args: { task: taskName },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadMyTasks();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}

function stopTimer(taskName) {
	frappe.call({
		method: 'lms.api.task.stop_timer',
		args: { task: taskName },
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				loadMyTasks();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}

function startElapsedTicker(tasks) {
	if (runningTimerTick) {
		clearInterval(runningTimerTick);
		runningTimerTick = null;
	}
	const running = tasks.filter(function(t) { return t.timer_running; });
	if (!running.length) return;

	runningTimerTick = setInterval(function() {
		running.forEach(function(task) {
			frappe.call({
				method: 'lms.api.task.get_task_detail',
				args: { name: task.name },
				callback: function(r) {
					if (!r.message || !r.message.success) return;
					const detail = r.message.data;
					const open = detail.timers.find(function(t) { return !t.ended_at; });
					const el = document.getElementById('time-' + task.name);
					if (open && el) {
						const elapsed = (Date.now() - new Date(open.started_at).getTime()) / 3600000;
						const total = (detail.total_time || 0) + elapsed;
						el.textContent = total.toFixed(2);
					}
				}
			});
		});
	}, 30000);
}

function loadHistory(page = 1) {
	frappe.call({
		method: 'lms.api.attendance.get_my_attendance',
		args: { page: page, page_size: 15 },
		callback: function(r) {
			const tbody = document.getElementById('attendance-history-tbody');
			tbody.innerHTML = '';
			if (!r.message || !r.message.success) return;

			r.message.data.forEach(function(att) {
				const tr = document.createElement('tr');
				tr.innerHTML = [
					'<td>' + att.attendance_date + '</td>',
					'<td>' + (att.check_in ? new Date(att.check_in).toLocaleTimeString() : '-') + '</td>',
					'<td>' + (att.check_out ? new Date(att.check_out).toLocaleTimeString() : '-') + '</td>',
					'<td>' + (att.work_hours || '0.00') + '</td>',
					'<td><span class="status-badge ' + String(att.status || '').toLowerCase().replace(/\s+/g, '_') + '">' + att.status + '</span></td>',
					'<td>' + (att.notes || '') + '</td>'
				].join('');
				tbody.appendChild(tr);
			});
		}
	});
}

function loadMyLeaves(page = 1) {
	frappe.call({
		method: 'lms.api.leave_request.get_my_leave_requests',
		args: { page: page, page_size: 10 },
		callback: function(r) {
			const tbody = document.getElementById('my-leaves-tbody');
			const empty = document.getElementById('my-leaves-empty');
			tbody.innerHTML = '';
			if (!r.message || !r.message.success || !r.message.data.length) {
				empty.style.display = 'block';
				return;
			}
			empty.style.display = 'none';

			r.message.data.forEach(function(lr) {
				const tr = document.createElement('tr');
				let actions = '';
				if (lr.status === 'Pending') {
					actions = '<button class="sw-btn sw-btn-danger sw-btn-sm" onclick="cancelLeave(\'' + lr.name + '\')">Cancel</button>';
				} else {
					actions = '<span class="lms-empty" style="padding:0">-</span>';
				}
				tr.innerHTML = [
					'<td>' + lr.leave_id + '</td>',
					'<td>' + lr.leave_type + '</td>',
					'<td>' + lr.from_date + '</td>',
					'<td>' + lr.to_date + '</td>',
					'<td><span class="status-badge ' + lr.status.toLowerCase() + '">' + lr.status + '</span></td>',
					'<td>' + actions + '</td>'
				].join('');
				tbody.appendChild(tr);
			});
		}
	});
}

function applyLeave() {
	const leaveType = document.getElementById('leave-type').value;
	const fromDate = document.getElementById('leave-from').value;
	const toDate = document.getElementById('leave-to').value;

	if (!leaveType || !fromDate || !toDate) {
		showError('Please select leave type and both dates.');
		return;
	}

	frappe.call({
		method: 'lms.api.leave_request.create_leave_request',
		args: {
			data: {
				leave_type: leaveType,
				from_date: fromDate,
				to_date: toDate
			}
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: r.message.message, indicator: 'green'});
				document.getElementById('leave-type').value = '';
				document.getElementById('leave-from').value = '';
				document.getElementById('leave-to').value = '';
				loadMyLeaves();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}

function cancelLeave(name) {
	frappe.call({
		method: 'lms.api.leave_request.update_leave_request',
		args: {
			name: name,
			data: { status: 'Canceled' }
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({message: 'Leave request canceled', indicator: 'green'});
				loadMyLeaves();
			} else if (r.message) {
				showError(r.message.message);
			}
		}
	});
}
